from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


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
    invocation_id: str
    provider: str
    operation: str
    method: str
    url: str
    status: int
    observed_at: str
    provider_request_id: str
    response_etag: str
    response_sha256: str


@dataclass(frozen=True)
class RuntimeVerification:
    status: str
    reason: str
    receipt_complete: bool
    content_match: bool
    git_blob_identity_match: bool
    binding_match: bool


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob_sha1(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def receipt_payload(receipt: InvocationReceipt) -> dict[str, object]:
    return {
        "provider": receipt.provider,
        "operation": receipt.operation,
        "method": receipt.method,
        "url": receipt.url,
        "status": receipt.status,
        "observed_at": receipt.observed_at,
        "provider_request_id": receipt.provider_request_id,
        "response_etag": receipt.response_etag,
        "response_sha256": receipt.response_sha256,
    }


def receipt_integrity_ok(receipt: InvocationReceipt) -> bool:
    expected_id = hashlib.sha256(
        json.dumps(
            receipt_payload(receipt),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return all(
        (
            receipt.invocation_id == expected_id,
            receipt.provider,
            receipt.operation,
            receipt.method == "GET",
            receipt.url,
            receipt.status == 200,
            receipt.observed_at,
            receipt.response_sha256,
        )
    )


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
    ) -> tuple[InvocationReceipt, bytes, bytes, str]:
        capability = self.capability()
        if capability.mode != "READ" or capability.authority != "READ_ONLY":
            raise PermissionError(
                "043c only permits read-only GitHub invocation"
            )

        encoded_path = quote(self.path, safe="/")
        encoded_ref = quote(self.ref, safe="")
        api_url = (
            f"https://api.github.com/repos/{self.repository}/contents/"
            f"{encoded_path}?ref={encoded_ref}"
        )
        raw_url = (
            f"https://raw.githubusercontent.com/{self.repository}/"
            f"{encoded_ref}/{encoded_path}"
        )
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "MORPHS-043c",
        }

        api = self.transport(api_url, headers)
        if api.status != 200:
            raise RuntimeError(
                f"GitHub contents API returned status {api.status}"
            )

        payload = json.loads(api.body.decode("utf-8"))
        if payload.get("type") != "file":
            raise RuntimeError(
                "GitHub contents API did not return a file resource"
            )
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
            raise RuntimeError(
                f"GitHub raw surface returned status {raw.status}"
            )

        receipt = InvocationReceipt(
            invocation_id="",
            provider=capability.provider,
            operation=capability.operation,
            method="GET",
            url=api_url,
            status=api.status,
            observed_at=api.observed_at,
            provider_request_id=api.headers.get("x-github-request-id", ""),
            response_etag=api.headers.get("etag", ""),
            response_sha256=sha256_hex(api.body),
        )
        receipt = InvocationReceipt(
            invocation_id=hashlib.sha256(
                json.dumps(
                    receipt_payload(receipt),
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest(),
            **receipt_payload(receipt),
        )
        return receipt, api_content, raw.body, str(payload["sha"])


def verify_runtime(
    adapter: GitHubRuntimeAdapter,
) -> tuple[InvocationReceipt, RuntimeVerification, dict[str, object]]:
    capability = adapter.capability()
    receipt, api_content, raw_content, provider_blob_sha = adapter.invoke()

    content_match = api_content == raw_content
    computed_blob_sha = git_blob_sha1(api_content)
    blob_identity_match = computed_blob_sha == provider_blob_sha
    receipt_complete = receipt_integrity_ok(receipt)

    binding_match = (
        adapter.repository in receipt.url
        and f"/{quote(adapter.path, safe='/')}?ref={quote(adapter.ref, safe='')}"
        in receipt.url
        and capability.identity_scope
        == f"{adapter.repository}@{adapter.ref}:{adapter.path}"
    )

    if not content_match:
        status = "DEFER"
        reason = "contents API and raw surface disagree"
    elif not blob_identity_match:
        status = "DEFER"
        reason = "provider blob identity does not match observed content"
    elif not receipt_complete:
        status = "DEFER"
        reason = "invocation receipt is incomplete or tampered"
    elif not binding_match:
        status = "DEFER"
        reason = "receipt is not bound to requested repository/path/ref"
    else:
        status = "VERIFIED"
        reason = (
            "runtime provider invocation, receipt integrity, independent raw "
            "read, and Git blob identity all agree"
        )

    return (
        receipt,
        RuntimeVerification(
            status=status,
            reason=reason,
            receipt_complete=receipt_complete,
            content_match=content_match,
            git_blob_identity_match=blob_identity_match,
            binding_match=binding_match,
        ),
        {
            "repository": adapter.repository,
            "path": adapter.path,
            "ref": adapter.ref,
            "provider_blob_sha": provider_blob_sha,
            "computed_git_blob_sha": computed_blob_sha,
            "contents_sha256": sha256_hex(api_content),
            "raw_sha256": sha256_hex(raw_content),
            "independent_surface": "raw.githubusercontent.com",
        },
    )


def run_experiment043c() -> dict[str, object]:
    adapter = GitHubRuntimeAdapter(
        repository="Loofy147/MORPHS",
        path="README.md",
        ref="main",
    )
    receipt, verification, identity = verify_runtime(adapter)

    result = {
        "experiment": "043c_real_runtime_adapter_and_receipt",
        "claim_state": (
            "EXPERIMENTALLY_SUPPORTED"
            if verification.status == "VERIFIED"
            else "UNKNOWN"
        ),
        "scope": (
            "real MORPHS Python runtime invoking public GitHub read-only endpoints "
            "for one repository file; independent same-provider raw read and Git blob identity check"
        ),
        "protocol": (
            "DISCOVER -> CLASSIFY -> BIND -> AUTHORIZE -> INVOKE -> RECEIPT "
            "-> INDEPENDENT_READ -> IDENTITY_VERIFY -> CLASSIFY"
        ),
        "runtime_integration": verification.status,
        "provider_independence": "NOT_ESTABLISHED",
        "invocation_receipt": receipt.__dict__,
        "verification": verification.__dict__,
        "identity": identity,
        "limitations": [
            "read-only provider operation",
            "public GitHub endpoints only",
            "same-provider independent surface, not provider-independent verification",
            "no external mutation",
            "no unknown network outcome",
            "no rollback",
        ],
        "next_boundary": (
            "043c-next: exercise the runtime adapter through the host capability registry "
            "and prove receipt persistence before any mutation attempt"
        ),
    }
    if verification.status != "VERIFIED":
        raise RuntimeError(
            json.dumps(result, indent=2, sort_keys=True)
        )
    return result


if __name__ == "__main__":
    print(json.dumps(run_experiment043c(), indent=2, sort_keys=True))
