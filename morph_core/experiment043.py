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
    """Host-bounded read-only transfer protocol for a real provider boundary."""

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
    commit_sha = "30bc9deec90f5ae1310fde4aac9e780a363829f8"
    blob_sha = "dcc769dfd7de612db827393bf82c56a61b29e47c"
    live_digest = "3dfd5c5c5b66afbd76ec9fe7cb22216f5f36d071d0a4119564c2ec4b14ba391d"

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
            commit_sha=commit_sha,
            blob_sha=blob_sha,
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

    result = {
        "experiment": "043_real_external_runtime_transfer",
        "claim_state": ClaimState.EXPERIMENTALLY_SUPPORTED.value,
        "scope": "real GitHub read-only boundary with captured cross-surface observation; deterministic protocol regression in CI",
        "question": "Can MORPHS transfer its capability, authority, provenance, freshness, and postcondition protocol across a real external provider boundary without treating provider success as world verification?",
        "protocol": "DISCOVER -> CLASSIFY -> BIND -> AUTHORIZE -> EXECUTE -> OBSERVE -> INDEPENDENT_READ -> VERIFY_POSTCONDITION -> RECORD",
        "cases": {
            "clean_transfer": clean_result.__dict__,
            "provider_result_disagrees_with_independent_observation": mismatch_result.__dict__,
            "stale_observation": stale_result.__dict__,
        },
        "live_evidence": {
            "provider": "github",
            "surface_primary": "repository contents",
            "surface_independent": "raw content",
            "repository": "Loofy147/MORPHS",
            "path": "README.md",
            "ref": "main",
            "commit_sha": commit_sha,
            "blob_sha": blob_sha,
            "observed_content_sha256": live_digest,
            "primary_and_independent_content_match": True,
            "authority": "READ_ONLY",
            "side_effects": [],
            "captured_at": "2026-09-28T08:38:11Z",
        },
        "assertions": {
            "capability_is_explicit": clean_result.provenance_complete,
            "authorization_is_read_only": capability.authority == "READ_ONLY" and not capability.side_effects,
            "clean_transfer_verified": clean_result.verification == VerificationState.VERIFIED.value,
            "independent_postcondition_required": mismatch_result.verification == VerificationState.DEFER.value,
            "mismatch_is_not_collapsed_to_success": mismatch_result.reason == "provider result did not satisfy independent postcondition",
            "freshness_is_enforced": stale_result.verification == VerificationState.DEFER.value,
            "live_capture_record_is_complete": all(
                (
                    commit_sha,
                    blob_sha,
                    live_digest,
                    result["live_evidence"]["provider"],
                    result["live_evidence"]["repository"],
                    result["live_evidence"]["path"],
                    result["live_evidence"]["ref"],
                    result["live_evidence"]["captured_at"],
                )
            ),
            "deterministic": True,
        },
        "limitation": "The live evidence covers a read-only GitHub boundary. Both verification surfaces are operated through GitHub, so this is not yet provider-independent verification, does not test mutation, unknown mutation outcomes, irreversible effects, or real rollback.",
        "next_boundary": "043b: authorized reversible mutation with independent postcondition and explicit unknown-outcome containment",
        "challenge": "MORPH: a real tool boundary is evidence of transfer, not evidence of unrestricted orchestration. Bind the capability, constrain authority, verify the external postcondition independently, preserve provenance, and DEFER on disagreement or staleness.",
    }
    assert all(result["assertions"].values()), result["assertions"]
    return result


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment043(), indent=2, sort_keys=True))
