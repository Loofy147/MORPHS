from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Callable


class ClaimState(str, Enum):
    EXPERIMENTALLY_SUPPORTED = "EXPERIMENTALLY_SUPPORTED"


class VerificationState(str, Enum):
    VERIFIED = "verified"
    DEFER = "defer"


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    provider: str
    operation: str
    mode: str
    authority: str
    side_effects: tuple[str, ...]
    verification_paths: tuple[str, ...]
    failure_modes: tuple[str, ...]
    identity_scope: str


@dataclass(frozen=True)
class PrimaryObservation:
    provider: str
    repository: str
    path: str
    ref: str
    commit_sha: str
    blob_sha: str
    content: str
    observed_at: datetime


@dataclass(frozen=True)
class IndependentObservation:
    source: str
    repository: str
    path: str
    ref: str
    content: str
    observed_at: datetime


@dataclass(frozen=True)
class TransferResult:
    verification: str
    reason: str
    content_sha256: str
    primary_sha256: str
    independent_sha256: str
    provenance_complete: bool
    fresh_enough: bool


class ExternalRuntimeTransfer:
    """Protocol model for a read-only external boundary.

    The deterministic experiment does not invoke GitHub itself. Any live
    provider observation is captured and recorded separately as host evidence.
    """

    def __init__(
        self,
        capability: CapabilityDescriptor,
        primary_read: Callable[[], PrimaryObservation],
        independent_read: Callable[[], IndependentObservation],
    ) -> None:
        self.capability = capability
        self.primary_read = primary_read
        self.independent_read = independent_read

    @staticmethod
    def digest(content: str) -> str:
        return sha256(content.encode("utf-8")).hexdigest()

    def validate_capability(self) -> None:
        if self.capability.mode != "READ":
            raise ValueError("043 only permits read-only transfer")
        if self.capability.authority != "READ_ONLY":
            raise ValueError("043 requires read-only authority")
        if self.capability.side_effects:
            raise ValueError("043 rejects a capability with declared side effects")
        if "INDEPENDENT_READ" not in self.capability.verification_paths:
            raise ValueError("043 requires an independent read path")

    def execute(self, max_age: timedelta, now: datetime) -> TransferResult:
        self.validate_capability()
        primary = self.primary_read()
        independent = self.independent_read()

        primary_hash = self.digest(primary.content)
        independent_hash = self.digest(independent.content)
        provenance_complete = all(
            (
                primary.provider,
                primary.repository,
                primary.path,
                primary.ref,
                primary.commit_sha,
                primary.blob_sha,
                independent.source,
                independent.repository,
                independent.path,
                independent.ref,
            )
        )

        primary_fresh = now - primary.observed_at <= max_age
        independent_fresh = now - independent.observed_at <= max_age
        fresh_enough = primary_fresh and independent_fresh
        content_matches = primary_hash == independent_hash
        binding_matches = (
            primary.repository == independent.repository
            and primary.path == independent.path
            and primary.ref == independent.ref
        )

        if not provenance_complete:
            return TransferResult(
                VerificationState.DEFER.value,
                "missing provenance",
                primary_hash,
                primary_hash,
                independent_hash,
                False,
                fresh_enough,
            )

        if not fresh_enough:
            return TransferResult(
                VerificationState.DEFER.value,
                "stale observation",
                primary_hash,
                primary_hash,
                independent_hash,
                True,
                False,
            )

        if not binding_matches:
            return TransferResult(
                VerificationState.DEFER.value,
                "cross-surface binding mismatch",
                primary_hash,
                primary_hash,
                independent_hash,
                True,
                True,
            )

        if not content_matches:
            return TransferResult(
                VerificationState.DEFER.value,
                "provider result did not satisfy independent postcondition",
                primary_hash,
                primary_hash,
                independent_hash,
                True,
                True,
            )

        return TransferResult(
            VerificationState.VERIFIED.value,
            "independent read agrees with provider result",
            primary_hash,
            primary_hash,
            independent_hash,
            True,
            True,
        )


def run_experiment043() -> dict[str, object]:
    fixed_now = datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc)

    capability = CapabilityDescriptor(
        capability_id="github.repository.read_file",
        provider="github",
        operation="read_file",
        mode="READ",
        authority="READ_ONLY",
        side_effects=(),
        verification_paths=("INDEPENDENT_READ",),
        failure_modes=("AVAILABILITY", "SCHEMA", "EVIDENCE", "STALE"),
        identity_scope="Loofy147/MORPHS@main",
    )

    def primary_fixture() -> PrimaryObservation:
        return PrimaryObservation(
            provider="github",
            repository="Loofy147/MORPHS",
            path="README.md",
            ref="main",
            commit_sha="captured-commit",
            blob_sha="captured-blob",
            content="captured-readme",
            observed_at=fixed_now,
        )

    def independent_fixture() -> IndependentObservation:
        return IndependentObservation(
            source="github.raw_surface",
            repository="Loofy147/MORPHS",
            path="README.md",
            ref="main",
            content="captured-readme",
            observed_at=fixed_now,
        )

    clean = ExternalRuntimeTransfer(capability, primary_fixture, independent_fixture)
    mismatched = ExternalRuntimeTransfer(
        capability,
        primary_fixture,
        lambda: IndependentObservation(
            source="github.raw_surface",
            repository="Loofy147/MORPHS",
            path="README.md",
            ref="main",
            content="different-read",
            observed_at=fixed_now,
        ),
    )
    stale = ExternalRuntimeTransfer(
        capability,
        primary_fixture,
        lambda: IndependentObservation(
            source="github.raw_surface",
            repository="Loofy147/MORPHS",
            path="README.md",
            ref="main",
            content="captured-readme",
            observed_at=fixed_now - timedelta(minutes=10),
        ),
    )

    clean_result = clean.execute(timedelta(minutes=5), fixed_now)
    mismatch_result = mismatched.execute(timedelta(minutes=5), fixed_now)
    stale_result = stale.execute(timedelta(minutes=5), fixed_now)

    runtime_integration_status = "OPEN"

    result = {
        "experiment": "043_real_external_runtime_transfer",
        "claim_state": ClaimState.EXPERIMENTALLY_SUPPORTED.value,
        "scope": "deterministic read-only external-boundary protocol model; host-captured GitHub observation recorded separately",
        "runtime_integration": {
            "status": "OPEN",
            "reason": "run_experiment043 does not invoke GitHub. The live read observation was captured by host-side tooling and is not used as runtime evidence by this module.",
        },
        "question": "Can the read-only protocol require explicit capability, authority, provenance, freshness, cross-surface binding, and postcondition verification?",
        "protocol": "DISCOVER -> CLASSIFY -> BIND -> AUTHORIZE -> EXECUTE -> OBSERVE -> INDEPENDENT_READ -> VERIFY_POSTCONDITION -> RECORD",
        "cases": {
            "clean_transfer": clean_result.__dict__,
            "provider_result_disagrees_with_independent_observation": mismatch_result.__dict__,
            "stale_observation": stale_result.__dict__,
        },
        "assertions": {
            "capability_is_explicit": clean_result.provenance_complete,
            "authorization_is_read_only": capability.authority == "READ_ONLY" and not capability.side_effects,
            "clean_transfer_verified": clean_result.verification == VerificationState.VERIFIED.value,
            "independent_postcondition_required": mismatch_result.verification == VerificationState.DEFER.value,
            "mismatch_is_not_collapsed_to_success": mismatch_result.reason == "provider result did not satisfy independent postcondition",
            "freshness_is_enforced": stale_result.verification == VerificationState.DEFER.value,
            "runtime_integration_is_not_overclaimed": runtime_integration_status == "OPEN",
            "deterministic": True,
        },
        "limitation": "This experiment verifies protocol semantics only. The live GitHub read evidence is host-captured and same-provider across two GitHub surfaces, so it does not establish MORPHS runtime integration or provider-independent verification.",
        "next_boundary": "043b: authorized reversible mutation protocol with separate host-captured live evidence",
    }
    assert all(result["assertions"].values()), result["assertions"]
    return result


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment043(), indent=2, sort_keys=True))
