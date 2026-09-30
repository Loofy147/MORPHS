from morph_core.experiment043c import (
    GitHubRuntimeAdapter,
    HttpObservation,
    git_blob_sha1,
    sha256_hex,
    verify_runtime,
)


def fake_transport_factory():
    content = b"MORPHS-043C\n"
    blob_sha = git_blob_sha1(content)
    payload = (
        '{"type":"file","encoding":"base64",'
        '"content":"TU9SUEhTLTA0M0MK","sha":"' + blob_sha + '"}'
    ).encode("utf-8")

    def transport(url, headers):
        if "api.github.com" in url:
            return HttpObservation(
                url=url,
                status=200,
                headers={"x-github-request-id": "fixture-request"},
                body=payload,
                observed_at="2026-09-30T00:00:00+00:00",
            )
        return HttpObservation(
            url=url,
            status=200,
            headers={},
            body=content,
            observed_at="2026-09-30T00:00:01+00:00",
        )

    return transport


def test_git_blob_identity_is_stable():
    content = b"hello"
    assert git_blob_sha1(content) == git_blob_sha1(content)


def test_runtime_verification_accepts_matching_surfaces():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    receipt, verification, identity = verify_runtime(adapter)
    assert verification.status == "VERIFIED"
    assert verification.receipt_complete is True
    assert receipt.status == 200
    assert identity["contents_sha256"] == identity["raw_sha256"]


def test_runtime_verification_rejects_content_mismatch():
    def transport(url, headers):
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
                observed_at="2026-09-30T00:00:00+00:00",
            )
        return HttpObservation(
            url=url,
            status=200,
            headers={},
            body=b"different",
            observed_at="2026-09-30T00:00:01+00:00",
        )

    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=transport,
    )
    _, verification, _ = verify_runtime(adapter)
    assert verification.status == "DEFER"
    assert verification.content_match is False


def test_runtime_verification_rejects_blob_identity_mismatch():
    def transport(url, headers):
        if "api.github.com" in url:
            content = b"api-content"
            payload = (
                '{"type":"file","encoding":"base64",'
                '"content":"YXBpLWNvbnRlbnQ=","sha":"wrong-blob"}'
            ).encode("utf-8")
            return HttpObservation(
                url=url,
                status=200,
                headers={"x-github-request-id": "fixture-request"},
                body=payload,
                observed_at="2026-09-30T00:00:00+00:00",
            )
        return HttpObservation(
            url=url,
            status=200,
            headers={},
            body=b"api-content",
            observed_at="2026-09-30T00:00:01+00:00",
        )

    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=transport,
    )
    _, verification, _ = verify_runtime(adapter)
    assert verification.status == "DEFER"
    assert verification.git_blob_identity_match is False


def test_runtime_verification_binds_resource_scope():
    adapter = GitHubRuntimeAdapter(
        "fixture/repo",
        "README.md",
        "main",
        transport=fake_transport_factory(),
    )
    _, verification, _ = verify_runtime(adapter)
    assert verification.binding_match is True


def test_digest_helpers_are_stable():
    assert sha256_hex(b"abc") == sha256_hex(b"abc")
