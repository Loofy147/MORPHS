from __future__ import annotations

import base64
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from morph_core.capability_registry import (
    AuthorizationState,
    HostCapabilityRegistry,
)


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    provider: str
    operation: str
    mode: str
    authority: str
    side_effects: tuple[str, ...]
    verification_paths: tuple[str, ...]
    identity_scope: str


@dataclass(frozen=True)
class HttpObservation:
    url: str
    status: int
    headers: dict[str, str]
    body: bytes
    observed_at: str


@dataclass(frozen=True)
class InvocationReceipt:
    receipt_version: int
    invocation_id: str
    execution_surface: str
    ci_run_id: str
    ci_head_sha: str
    capability_id: str
    identity_scope: str
    provider: str
    operation: str
    method: str
    url: str
    status: int
    observed_at: str
    provider_request_id: str
    response_etag: str
    response_sha256: str
    raw_url: str
    raw_status: int
    raw_observed_at: str
    raw_request_id: str
    raw_response_sha256: str
    ref_requested: str
    ref_resolved_commit: str
    ref_resolution_url: str
    ref_resolution_status: int
    ref_resolution_request_id: str


@dataclass(frozen=True)
class RuntimeVerification:
    status: str
    reason: str
    receipt_complete: bool
    receipt_self_consistent: bool
    content_match: bool
    git_blob_identity_match: bool
    binding_match: bool
    fresh_enough: bool


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def receipt_payload(receipt: InvocationReceipt) -> dict[str, object]:
    return {
        "receipt_version": receipt.receipt_version,
        "execution_surface": receipt.execution_surface,
        "ci_run_id": receipt.ci_run_id,
        "ci_head_sha": receipt.ci_head_sha,
        "capability_id": receipt.capability_id,
        "identity_scope": receipt.identity_scope,
        "provider": receipt.provider,
        "operation": receipt.operation,
        "method": receipt.method,
        "url": receipt.url,
        "status": receipt.status,
        "observed_at": receipt.observed_at,
        "provider_request_id": receipt.provider_request_id,
        "response_etag": receipt.response_etag,
        "response_sha256": receipt.response_sha256,
        "raw_url": receipt.raw_url,
        "raw_status": receipt.raw_status,
        "raw_observed_at": receipt.raw_observed_at,
        "raw_request_id": receipt.raw_request_id,
        "raw_response_sha256": receipt.raw_response_sha256,
        "ref_requested": receipt.ref_requested,
        "ref_resolved_commit": receipt.ref_resolved_commit,
        "ref_resolution_url": receipt.ref_resolution_url,
        "ref_resolution_status": receipt.ref_resolution_status,
        "ref_resolution_request_id": receipt.ref_resolution_request_id,
    }


def receipt_self_consistency_ok(receipt: InvocationReceipt) -> bool:
    expected_id = hashlib.sha256(
        json.dumps(
            receipt_payload(receipt),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return receipt.invocation_id == expected_id


def verify_persisted_receipt(
    path: str | Path,
    expected_run_id: str | None = None,
    expected_head_sha: str | None = None,
) -> dict[str, object]:
    raw = Path(path).read_bytes()
    document = json.loads(raw.decode("utf-8"))
    receipt = InvocationReceipt(
        invocation_id=document["invocation_id"],
        **document["receipt"],
    )
    self_consistent = receipt_self_consistency_ok(receipt)
    run_match = expected_run_id is None or receipt.ci_run_id == expected_run_id
    head_match = expected_head_sha is None or receipt.ci_head_sha == expected_head_sha
    document_flag = document.get("receipt_self_consistent") is True
    return {
        "file_sha256": sha256_hex(raw),
        "self_consistent": self_consistent,
        "document_flag": document_flag,
        "run_match": run_match,
        "head_match": head_match,
        "verified": all(
            (self_consistent, document_flag, run_match, head_match)
        ),
    }




class JsonReceiptStore:
    """Durable-at-run persistence for a runtime invocation receipt.

    CI uploads this file as an artifact. This is persistence of the observed
    receipt, not cryptographic authenticity against a privileged artifact writer.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def persist(self, receipt: InvocationReceipt) -> dict[str, str]:
        payload = {
            "receipt": receipt_payload(receipt),
            "invocation_id": receipt.invocation_id,
            "receipt_self_consistent": receipt_self_consistency_ok(receipt),
        }
        encoded = json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(encoded)
        return {
            "path": str(self.path),
            "artifact_sha256": sha256_hex(encoded),
        }


class GitHubRuntimeAdapter:
    """Real read-only provider adapter used by the 043c CI experiment."""

    def __init__(
        self,
        repository: str,
        path: str,
        ref: str,
        transport: Callable[[str, dict[str, str]], HttpObservation] | None = None,
    ) -> None:
        self.repository = repository
        self.path = path
        self.ref = ref
        self.transport = transport or self._http_get

    @staticmethod
    def _http_get(url: str, headers: dict[str, str]) -> HttpObservation:
        request = Request(url, headers=headers, method="GET")
        observed_at = datetime.now(timezone.utc).isoformat()
        try:
            with urlopen(request, timeout=15) as response:
                body = response.read()
                response_headers = {
                    key.lower(): value
                    for key, value in response.headers.items()
                }
                return HttpObservation(
                    url=url,
                    status=response.status,
                    headers=response_headers,
                    body=body,
                    observed_at=observed_at,
                )
        except HTTPError as exc:
            body = exc.read()
            raise RuntimeError(
                f"external provider HTTP failure {exc.code} for {url}: {body[:200]!r}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                f"external provider transport failure for {url}: {exc}"
            ) from exc

    def capability(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(
            capability_id="github.repository.read_file",
            provider="github",
            operation="read_file",
            mode="READ",
            authority="READ_ONLY",
            side_effects=(),
            verification_paths=("GITHUB_CONTENTS_API", "GITHUB_RAW"),
            identity_scope=f"{self.repository}@{self.ref}:{self.path}",
        )

    def invoke(
        self,
    ) -> tuple[
        InvocationReceipt,
        bytes,
        bytes,
        str,
        HttpObservation,
        HttpObservation,
    ]:
        capability = self.capability()
        if capability.mode != "READ" or capability.authority != "READ_ONLY":
            raise PermissionError("043c only permits read-only GitHub invocation")

        encoded_path = quote(self.path, safe="/")
        encoded_ref = quote(self.ref, safe="")

        api_headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "MORPHS-043c",
        }

        ref_resolution_url = (
            f"https://api.github.com/repos/{self.repository}/commits/{encoded_ref}"
        )
        ref_resolution = self.transport(ref_resolution_url, api_headers)
        if ref_resolution.status != 200:
            raise RuntimeError(
                f"GitHub ref resolution returned status {ref_resolution.status}"
            )
        if ref_resolution.url != ref_resolution_url:
            raise RuntimeError("ref-resolution response URL mismatch")

        ref_payload = json.loads(ref_resolution.body.decode("utf-8"))
        resolved_commit = str(ref_payload["sha"])
        if not resolved_commit:
            raise RuntimeError("GitHub ref resolution returned no commit SHA")

        api_url = (
            f"https://api.github.com/repos/{self.repository}/contents/"
            f"{encoded_path}?ref={quote(resolved_commit, safe='')}"
        )
        raw_url = (
            f"https://raw.githubusercontent.com/{self.repository}/"
            f"{quote(resolved_commit, safe='')}/{encoded_path}"
        )

        api = self.transport(api_url, api_headers)
        if api.status != 200:
            raise RuntimeError(f"GitHub contents API returned status {api.status}")
        if api.url != api_url:
            raise RuntimeError("contents response URL mismatch")

        payload = json.loads(api.body.decode("utf-8"))
        if payload.get("type") != "file":
            raise RuntimeError("GitHub contents API did not return a file resource")
        if payload.get("encoding") != "base64":
            raise RuntimeError(
                "GitHub contents API returned an unexpected encoding"
            )

        api_content = base64.b64decode(
            payload["content"].replace("\n", ""),
            validate=True,
        )

        raw = self.transport(
            raw_url,
            {"User-Agent": "MORPHS-043c"},
        )
        if raw.status != 200:
            raise RuntimeError(f"GitHub raw surface returned status {raw.status}")
        if raw.url != raw_url:
            raise RuntimeError("raw response URL mismatch")

        receipt = InvocationReceipt(
            receipt_version=1,
            invocation_id="",
            execution_surface="MORPHS_PYTHON_RUNTIME",
            ci_run_id=os.environ.get("GITHUB_RUN_ID", "LOCAL"),
            ci_head_sha=os.environ.get("GITHUB_SHA", "LOCAL"),
            capability_id=capability.capability_id,
            identity_scope=capability.identity_scope,
            provider=capability.provider,
            operation=capability.operation,
            method="GET",
            url=api.url,
            status=api.status,
            observed_at=api.observed_at,
            provider_request_id=api.headers.get("x-github-request-id", ""),
            response_etag=api.headers.get("etag", ""),
            response_sha256=sha256_hex(api.body),
            raw_url=raw.url,
            raw_status=raw.status,
            raw_observed_at=raw.observed_at,
            raw_request_id=raw.headers.get("x-github-request-id", ""),
            raw_response_sha256=sha256_hex(raw.body),
            ref_requested=self.ref,
            ref_resolved_commit=resolved_commit,
            ref_resolution_url=ref_resolution.url,
            ref_resolution_status=ref_resolution.status,
            ref_resolution_request_id=ref_resolution.headers.get(
                "x-github-request-id",
                "",
            ),
        )
        invocation_id = hashlib.sha256(
            json.dumps(
                receipt_payload(receipt),
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        receipt = InvocationReceipt(
            invocation_id=invocation_id,
            **receipt_payload(receipt),
        )
        return (
            receipt,
            api_content,
            raw.body,
            str(payload["sha"]),
            api,
            raw,
        )


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def verify_runtime(
    adapter: GitHubRuntimeAdapter,
    registry: HostCapabilityRegistry | None = None,
    receipt_store: JsonReceiptStore | None = None,
    now: datetime | None = None,
    max_age: timedelta = timedelta(seconds=60),
) -> tuple[InvocationReceipt, RuntimeVerification, dict[str, object]]:
    capability = adapter.capability()
    if registry is None:
        raise PermissionError(
            "043c requires an explicit host capability registry"
        )
    host_registry = registry
    resolved_binding = host_registry.resolve(capability.capability_id)
    if resolved_binding.descriptor != capability:
        raise RuntimeError("registry capability binding does not match the adapter capability")

    (
        receipt,
        api_content,
        raw_content,
        provider_blob_sha,
        api_observation,
        raw_observation,
    ) = host_registry.invoke(
        capability.capability_id,
        capability.identity_scope,
    )

    persistence = None
    persistence_verification = None
    if receipt_store is not None:
        persistence = receipt_store.persist(receipt)
        persistence_verification = verify_persisted_receipt(
            receipt_store.path,
            expected_run_id=receipt.ci_run_id,
            expected_head_sha=receipt.ci_head_sha,
        )
        if persistence_verification["file_sha256"] != persistence["artifact_sha256"]:
            raise RuntimeError("persisted receipt hash changed after write")
        if not persistence_verification["verified"]:
            raise RuntimeError(
                "persisted receipt failed revalidation"
            )

    expected_api_url = (
        f"https://api.github.com/repos/{adapter.repository}/contents/"
        f"{quote(adapter.path, safe='/')}"
        f"?ref={quote(receipt.ref_resolved_commit, safe='')}"
    )
    expected_raw_url = (
        f"https://raw.githubusercontent.com/{adapter.repository}/"
        f"{quote(receipt.ref_resolved_commit, safe='')}/"
        f"{quote(adapter.path, safe='/')}"
    )
    current_time = now or datetime.now(timezone.utc)
    api_age = current_time - _parse_time(api_observation.observed_at)
    raw_age = current_time - _parse_time(raw_observation.observed_at)
    fresh_enough = (
        api_age >= timedelta(0)
        and raw_age >= timedelta(0)
        and api_age <= max_age
        and raw_age <= max_age
    )

    content_match = api_content == raw_content
    computed_blob_sha = git_blob_sha1(api_content)
    blob_identity_match = computed_blob_sha == provider_blob_sha
    receipt_complete = all(
        (
            receipt.execution_surface == "MORPHS_PYTHON_RUNTIME",
            receipt.ci_run_id,
            receipt.ci_head_sha,
            receipt.capability_id,
            receipt.identity_scope,
            receipt.provider_request_id,
            receipt.ref_resolution_request_id,
            receipt.url,
            receipt.raw_url,
            receipt.raw_observed_at,
            receipt.response_sha256,
            receipt.raw_response_sha256,
            receipt.ref_resolved_commit,
        )
    )
    receipt_self_consistent = receipt_self_consistency_ok(receipt)
    binding_match = all(
        (
            receipt.capability_id == capability.capability_id,
            receipt.identity_scope == capability.identity_scope,
            receipt.url == expected_api_url,
            receipt.raw_url == expected_raw_url,
            api_observation.url == expected_api_url,
            raw_observation.url == expected_raw_url,
            receipt.ref_requested == adapter.ref,
            receipt.ref_resolution_url.endswith(
                f"/commits/{quote(adapter.ref, safe='')}"
            ),
            capability.identity_scope
            == f"{adapter.repository}@{adapter.ref}:{adapter.path}",
        )
    )

    if not fresh_enough:
        status = "DEFER"
        reason = "runtime observations exceed the freshness budget"
    elif not content_match:
        status = "DEFER"
        reason = (
            "contents API and raw surface disagree at the same resolved commit"
        )
    elif not blob_identity_match:
        status = "DEFER"
        reason = "provider blob identity does not match observed content"
    elif not receipt_complete or not receipt_self_consistent:
        status = "DEFER"
        reason = "invocation receipt is incomplete or self-inconsistent"
    elif not binding_match:
        status = "DEFER"
        reason = "receipt or provider observation is not bound to the requested capability/resource"
    else:
        status = "VERIFIED"
        reason = (
            "runtime provider invocation, registry binding, receipt self-consistency, "
            "fresh same-commit cross-surface read, and Git blob identity all agree"
        )

    return (
        receipt,
        RuntimeVerification(
            status=status,
            reason=reason,
            receipt_complete=receipt_complete,
            receipt_self_consistent=receipt_self_consistent,
            content_match=content_match,
            git_blob_identity_match=blob_identity_match,
            binding_match=binding_match,
            fresh_enough=fresh_enough,
        ),
        {
            "repository": adapter.repository,
            "path": adapter.path,
            "ref": adapter.ref,
            "resolved_commit": receipt.ref_resolved_commit,
            "provider_blob_sha": provider_blob_sha,
            "computed_git_blob_sha": computed_blob_sha,
            "contents_sha256": sha256_hex(api_content),
            "raw_sha256": sha256_hex(raw_content),
            "independent_surface": "raw.githubusercontent.com",
            "api_observed_at": api_observation.observed_at,
            "raw_observed_at": raw_observation.observed_at,
            "max_age_seconds": int(max_age.total_seconds()),
            "receipt_artifact": persistence,
            "receipt_artifact_revalidation": persistence_verification,
            "provider_independence": "NOT_ESTABLISHED",
            "receipt_authenticity": "OPEN",
        },
    )


def run_experiment043c(
    registry: HostCapabilityRegistry,
    receipt_store: JsonReceiptStore | None = None,
) -> dict[str, object]:
    """Run 043c only with a registry injected by the host layer."""
    adapter = GitHubRuntimeAdapter(
        repository="Loofy147/MORPHS",
        path="README.md",
        ref="main",
    )
    if receipt_store is None:
        receipt_store = JsonReceiptStore(
            os.environ.get(
                "MORPHS_043C_RECEIPT_PATH",
                "experiments/043c/runtime_receipt.json",
            )
        )

    receipt, verification, identity = verify_runtime(
        adapter,
        registry=registry,
        receipt_store=receipt_store,
    )

    result = {
        "experiment": "043c_real_runtime_adapter_and_receipt",
        "claim_state": (
            "EXPERIMENTALLY_SUPPORTED"
            if verification.status == "VERIFIED"
            else "UNKNOWN"
        ),
        "scope": (
            "real MORPHS Python runtime invoking public GitHub read-only endpoints "
            "for one repository file; ref is resolved to an exact commit before "
            "the contents and raw reads"
        ),
        "protocol": (
            "DISCOVER -> RESOLVE_REF -> REGISTRY_BIND -> AUTHORIZE -> INVOKE "
            "-> RECEIPT_PERSIST -> INDEPENDENT_READ -> IDENTITY_VERIFY -> CLASSIFY"
        ),
        "runtime_integration": verification.status,
        "authority_integration": (
            "INJECTED_HOST_REGISTRY"
        ),
        "invocation_receipt": receipt.__dict__,
        "verification": verification.__dict__,
        "identity": identity,
        "limitations": [
            "read-only provider operation",
            "public GitHub endpoints only",
            "same-provider independent surface, not provider-independent verification",
            "receipt authenticity is OPEN because the receipt is hash-self-consistent but not signed",
            "host registry is an experimental in-process boundary, not a production isolation mechanism",
            "no external mutation",
            "no unknown network outcome",
            "no rollback",
        ],
        "next_boundary": (
            "043c-next: provider-independent verification or controlled "
            "unknown-outcome handling; runtime mutation remains blocked"
        ),
    }
    if verification.status != "VERIFIED":
        raise RuntimeError(json.dumps(result, indent=2, sort_keys=True))
    return result

if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment043c(), indent=2, sort_keys=True))
