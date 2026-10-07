from dataclasses import replace
import hashlib
import json
import os
from datetime import datetime, timezone

import pytest

from morph_core.capability_registry import AuthorizationState, HostCapabilityRegistry
from morph_core.experiment043c_host import build_host_registry
from morph_core.experiment043c import (
    GitHubRuntimeAdapter,
    HttpObservation,
    JsonReceiptStore,
    git_blob_sha1,
    receipt_self_consistency_ok,
    sha256_hex,
    verify_persisted_receipt,
    verify_runtime,
    run_experiment043c,
)


def allowed_registry(adapter):
    registry = HostCapabilityRegistry()
    registry.register(
        adapter.capability(),
        adapter.invoke,
        AuthorizationState.ALLOW,
        require_bound_invoker=True,
    )
    return registry


def fake_transport_factory(
    raw_url_override=None,
    raw_observed_at="2026-09-30T00:00:02+00:00",
):
    content = b"MORPHS-043C\n"
    blob_sha = git_blob_sha1(content)
    resolved_commit = "fixture-commit"
    content_payload = (
        '{"type":"file","encoding":"base64",'
        '"content":"TU9SUEhTLTA0M0MK","sha":"' + blob_sha + '"}'
    ).encode("utf-8")
    commit_payload = ('{"sha":"' + resolved_commit + '"}').encode("utf-8")

    def transport(url, headers):
        if "/commits/main" in url:
            return HttpObservation(
                url=url,
                status=200,
                headers={"x-github-request-id": "commit-request"},
                body=commit_payload,
                observed_at="2026-09-30T00:00:00+00:00",
            )
        if "api.github.com" in url:
            return HttpObservation(
                url=url,
                status=200,
                headers={"x-github-request-id": "fixture-request"},
                body=content_payload,
                observed_at="2026-09-30T00:00:01+00:00",
            )
        return HttpObservation(
            url=raw_url_override or url,
            status=200,
            headers={},
            body=content,
            observed_at=raw_observed_at,
        )

    return transport


def fixed_now():
    return datetime(2026, 9, 30, 0, 0, 3, tzinfo=timezone.utc)


def test_git_blob_identity_is_stable():
    content = b"hello"
    assert git_blob_sha1(content) == git_blob_sha1(content)


def test_runtime_requires_explicit_host_registry():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    with pytest.raises(PermissionError, match="explicit host capability registry"):
        verify_runtime(adapter, now=fixed_now())


def test_runtime_verification_accepts_matching_surfaces(monkeypatch):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GITHUB_RUN_ID", "12345")
    monkeypatch.setenv("GITHUB_SHA", "a" * 40)
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    receipt, verification, identity = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert verification.status == "VERIFIED"
    assert verification.receipt_complete is True
    assert verification.receipt_self_consistent is True
    assert verification.fresh_enough is True
    assert receipt.status == 200
    assert receipt.ref_requested == "main"
    assert receipt.ref_resolved_commit == "fixture-commit"
    assert receipt.capability_id == "github.repository.read_file"
    assert receipt.identity_scope == "fixture/repo@main:README.md"
    assert receipt.execution_surface == "MORPHS_PYTHON_RUNTIME"
    assert receipt.ci_run_id == os.environ.get("GITHUB_RUN_ID", "LOCAL")
    assert receipt.ci_head_sha == os.environ.get("GITHUB_SHA", "LOCAL")
    assert identity["contents_sha256"] == identity["raw_sha256"]
    assert identity["trusted_ci_context"] is True


def test_runtime_verification_is_not_promoted_locally(monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    _, verification, identity = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert verification.status == "DEFER"
    assert identity["trusted_ci_context"] is False


def test_runtime_verification_binds_both_surfaces_to_resolved_commit():
    seen = []
    transport = fake_transport_factory()

    def recording_transport(url, headers):
        seen.append(url)
        return transport(url, headers)

    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=recording_transport,
    )
    verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert any("/commits/main" in url for url in seen)
    assert any("ref=fixture-commit" in url for url in seen)
    assert any("/fixture-commit/README.md" in url for url in seen)


def test_receipt_tampering_is_detectable():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    receipt, _, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert receipt_self_consistency_ok(receipt) is True
    tampered_hash = replace(receipt, response_sha256="tampered")
    tampered_capability = replace(receipt, capability_id="other.capability")
    tampered_runtime = replace(
        receipt,
        execution_surface="OTHER_RUNTIME",
    )
    assert receipt_self_consistency_ok(tampered_hash) is False
    assert receipt_self_consistency_ok(tampered_capability) is False
    assert receipt_self_consistency_ok(tampered_runtime) is False


def test_receipt_persistence_is_hash_bound(tmp_path):
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    receipt, _, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        receipt_store=JsonReceiptStore(tmp_path / "receipt.json"),
        now=fixed_now(),
    )
    saved = (tmp_path / "receipt.json").read_bytes()
    assert b"fixture/repo@main:README.md" in saved
    assert sha256_hex(saved)
    assert receipt.invocation_id.encode() in saved


def test_registry_denial_prevents_runtime_invocation():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    registry = HostCapabilityRegistry()
    registry.register(
        adapter.capability(),
        adapter.invoke,
        AuthorizationState.DENY,
    )
    with pytest.raises(PermissionError):
        verify_runtime(
            adapter,
            registry=registry,
            now=fixed_now(),
        )


def test_runtime_verification_rejects_content_mismatch():
    transport = fake_transport_factory()

    def mismatch_transport(url, headers):
        if "/commits/main" in url:
            return transport(url, headers)
        if "api.github.com" in url:
            content = b"api-content"
            payload = (
                '{"type":"file","encoding":"base64",'
                '"content":"YXBpLWNvbnRlbnQ=","sha":"'
                + git_blob_sha1(content)
                + '"}'
            ).encode("utf-8")
            return HttpObservation(
                url=url,
                status=200,
                headers={"x-github-request-id": "fixture-request"},
                body=payload,
                observed_at="2026-09-30T00:00:01+00:00",
            )
        return HttpObservation(
            url=url,
            status=200,
            headers={},
            body=b"different",
            observed_at="2026-09-30T00:00:02+00:00",
        )

    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=mismatch_transport,
    )
    _, verification, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert verification.status == "DEFER"
    assert verification.content_match is False


def test_runtime_verification_rejects_blob_identity_mismatch():
    transport = fake_transport_factory()

    def mismatch_transport(url, headers):
        if "/commits/main" in url:
            return transport(url, headers)
        if "api.github.com" in url:
            payload = (
                '{"type":"file","encoding":"base64",'
                '"content":"YXBpLWNvbnRlbnQ=","sha":"wrong-blob"}'
            ).encode("utf-8")
            return HttpObservation(
                url=url,
                status=200,
                headers={"x-github-request-id": "fixture-request"},
                body=payload,
                observed_at="2026-09-30T00:00:01+00:00",
            )
        return HttpObservation(
            url=url,
            status=200,
            headers={},
            body=b"api-content",
            observed_at="2026-09-30T00:00:02+00:00",
        )

    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=mismatch_transport,
    )
    _, verification, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert verification.status == "DEFER"
    assert verification.git_blob_identity_match is False


def test_runtime_verification_rejects_wrong_response_source():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(
            raw_url_override=(
                "https://raw.githubusercontent.com/other/repo/"
                "fixture-commit/README.md"
            )
        ),
    )
    with pytest.raises(RuntimeError, match="raw response URL mismatch"):
        verify_runtime(
            adapter,
            registry=allowed_registry(adapter),
            now=fixed_now(),
        )


def test_runtime_verification_rejects_stale_observation():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(
            raw_observed_at="2026-09-29T23:00:00+00:00"
        ),
    )
    _, verification, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        now=fixed_now(),
    )
    assert verification.status == "DEFER"
    assert verification.fresh_enough is False


def test_digest_helpers_are_stable():
    assert sha256_hex(b"abc") == sha256_hex(b"abc")


def test_registry_rejects_mismatched_adapter_invoker():
    primary = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    other = GitHubRuntimeAdapter(
        "fixture/other",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    registry = HostCapabilityRegistry()
    with pytest.raises(ValueError, match="descriptor mismatch"):
        registry.register(
            primary.capability(),
            other.invoke,
            AuthorizationState.ALLOW,
            require_bound_invoker=True,
        )


def test_persisted_receipt_revalidation_detects_tamper(tmp_path):
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    store = JsonReceiptStore(tmp_path / "receipt.json")
    receipt, _, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        receipt_store=store,
        now=fixed_now(),
    )
    good = verify_persisted_receipt(
        store.path,
        expected_run_id=receipt.ci_run_id,
        expected_head_sha=receipt.ci_head_sha,
    )
    assert good["verified"] is True

    raw = store.path.read_text()
    tampered = raw.replace("github.repository.read_file", "other.capability")
    store.path.write_text(tampered)
    bad = verify_persisted_receipt(
        store.path,
        expected_run_id=receipt.ci_run_id,
        expected_head_sha=receipt.ci_head_sha,
    )
    assert bad["verified"] is False


def test_experiment_requires_injected_host_registry(monkeypatch):
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    with pytest.raises(TypeError):
        run_experiment043c()  # registry injection is mandatory


def test_host_runner_requires_explicit_allow(monkeypatch):
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    monkeypatch.delenv("MORPHS_043C_AUTHORIZATION", raising=False)
    with pytest.raises(PermissionError, match="explicit MORPHS_043C_AUTHORIZATION=ALLOW"):
        build_host_registry(adapter)


def test_host_runner_requires_bound_invoker(monkeypatch):
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    monkeypatch.setenv("MORPHS_043C_AUTHORIZATION", "ALLOW")
    registry = build_host_registry(adapter)
    assert registry.resolve(adapter.capability().capability_id).descriptor == adapter.capability()


def test_persisted_receipt_replay_with_recomputed_self_hash_is_detected(tmp_path):
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    store = JsonReceiptStore(tmp_path / "receipt.json")
    receipt, _, _ = verify_runtime(
        adapter,
        registry=allowed_registry(adapter),
        receipt_store=store,
        now=fixed_now(),
    )

    document = json.loads(store.path.read_text())
    document["receipt"]["ci_run_id"] = "attacker-run"
    document["receipt"]["ci_head_sha"] = "attacker-head"
    payload = document["receipt"]
    document["invocation_id"] = hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    document["receipt_self_consistent"] = True
    store.path.write_text(json.dumps(document, sort_keys=True))

    verification = verify_persisted_receipt(
        store.path,
        expected_run_id=receipt.ci_run_id,
        expected_head_sha=receipt.ci_head_sha,
    )
    assert verification["self_consistent"] is True
    assert verification["run_match"] is False
    assert verification["head_match"] is False
    assert verification["verified"] is False
