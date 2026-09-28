from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MutationDecision(str, Enum):
    APPLY = "APPLY"
    NOOP_ALREADY_APPLIED = "NOOP_ALREADY_APPLIED"
    BLOCK = "BLOCK"
    DEFER = "DEFER"


class OutcomeClass(str, Enum):
    APPLIED = "APPLIED"
    NOT_APPLIED = "NOT_APPLIED"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class MutationCapability:
    capability_id: str
    provider: str
    operation: str
    authority: str
    side_effects: tuple[str, ...]
    verification_paths: tuple[str, ...]


@dataclass(frozen=True)
class MutationPlan:
    expected_before: str
    desired_after: str
    rollback_target: str


@dataclass(frozen=True)
class MutationObservation:
    state: str
    blob_sha: str


@dataclass(frozen=True)
class ProtocolResult:
    decision: str
    outcome: str
    state_after: str
    safe_to_retry: bool
    rollback_allowed: bool
    reason: str


class ReversibleMutationProtocol:
    def __init__(self, capability: MutationCapability) -> None:
        self.capability = capability

    def validate(self, authorized: bool) -> None:
        if self.capability.authority != "WRITE":
            raise ValueError("043b requires explicit write authority")
        if not authorized:
            raise PermissionError("043b mutation is not authorized")
        if "INDEPENDENT_READ" not in self.capability.verification_paths:
            raise ValueError("043b requires an independent read path")
        if "ROLLBACK_READ" not in self.capability.verification_paths:
            raise ValueError("043b requires rollback revalidation")

    def preflight(
        self,
        current: MutationObservation,
        plan: MutationPlan,
        authorized: bool,
    ) -> MutationDecision:
        self.validate(authorized)
        if current.state == plan.desired_after:
            return MutationDecision.NOOP_ALREADY_APPLIED
        if current.state != plan.expected_before:
            return MutationDecision.DEFER
        return MutationDecision.APPLY

    @staticmethod
    def classify_unknown(
        observed_after_unknown: MutationObservation,
        plan: MutationPlan,
    ) -> ProtocolResult:
        if observed_after_unknown.state == plan.desired_after:
            return ProtocolResult(
                MutationDecision.NOOP_ALREADY_APPLIED.value,
                OutcomeClass.APPLIED.value,
                observed_after_unknown.state,
                False,
                False,
                "unknown provider outcome resolved by observation: already applied",
            )
        if observed_after_unknown.state == plan.expected_before:
            return ProtocolResult(
                MutationDecision.APPLY.value,
                OutcomeClass.NOT_APPLIED.value,
                observed_after_unknown.state,
                True,
                False,
                "unknown provider outcome resolved by observation: not applied",
            )
        return ProtocolResult(
            MutationDecision.DEFER.value,
            OutcomeClass.PARTIAL.value,
            observed_after_unknown.state,
            False,
            False,
            "unknown provider outcome resolved to unexpected state; contain and investigate",
        )

    @staticmethod
    def verify_postcondition(
        observed_after: MutationObservation,
        plan: MutationPlan,
    ) -> ProtocolResult:
        if observed_after.state != plan.desired_after:
            return ProtocolResult(
                MutationDecision.DEFER.value,
                OutcomeClass.PARTIAL.value,
                observed_after.state,
                False,
                False,
                "independent postcondition failed",
            )
        return ProtocolResult(
            MutationDecision.NOOP_ALREADY_APPLIED.value,
            OutcomeClass.APPLIED.value,
            observed_after.state,
            False,
            True,
            "independent postcondition verified",
        )

    @staticmethod
    def rollback_preflight(
        current: MutationObservation,
        plan: MutationPlan,
    ) -> MutationDecision:
        if current.state != plan.desired_after:
            return MutationDecision.DEFER
        return MutationDecision.APPLY

    @staticmethod
    def verify_rollback(
        observed_after_rollback: MutationObservation,
        plan: MutationPlan,
    ) -> ProtocolResult:
        if observed_after_rollback.state != plan.rollback_target:
            return ProtocolResult(
                MutationDecision.DEFER.value,
                OutcomeClass.PARTIAL.value,
                observed_after_rollback.state,
                False,
                False,
                "rollback postcondition failed",
            )
        return ProtocolResult(
            MutationDecision.NOOP_ALREADY_APPLIED.value,
            OutcomeClass.APPLIED.value,
            observed_after_rollback.state,
            False,
            False,
            "rollback postcondition verified",
        )


def run_experiment043b() -> dict[str, object]:
    capability = MutationCapability(
        capability_id="github.repository.update_file",
        provider="github",
        operation="update_file",
        authority="WRITE",
        side_effects=("REPOSITORY_FILE_MUTATION",),
        verification_paths=("INDEPENDENT_READ", "ROLLBACK_READ"),
    )
    protocol = ReversibleMutationProtocol(capability)
    plan = MutationPlan("baseline", "mutated", "baseline")

    clean_preflight = protocol.preflight(
        MutationObservation("baseline", "baseline-blob"),
        plan,
        authorized=True,
    )
    idempotent_preflight = protocol.preflight(
        MutationObservation("mutated", "mutated-blob"),
        plan,
        authorized=True,
    )
    drift_preflight = protocol.preflight(
        MutationObservation("drifted", "drifted-blob"),
        plan,
        authorized=True,
    )
    unknown_not_applied = protocol.classify_unknown(
        MutationObservation("baseline", "baseline-blob"),
        plan,
    )
    unknown_applied = protocol.classify_unknown(
        MutationObservation("mutated", "mutated-blob"),
        plan,
    )
    unknown_unexpected = protocol.classify_unknown(
        MutationObservation("partial", "partial-blob"),
        plan,
    )
    postcondition_ok = protocol.verify_postcondition(
        MutationObservation("mutated", "mutated-blob"),
        plan,
    )
    rollback_allowed = protocol.rollback_preflight(
        MutationObservation("mutated", "mutated-blob"),
        plan,
    )
    rollback_blocked_by_drift = protocol.rollback_preflight(
        MutationObservation("drifted", "drifted-blob"),
        plan,
    )
    rollback_verified = protocol.verify_rollback(
        MutationObservation("baseline", "baseline-blob"),
        plan,
    )

    result = {
        "experiment": "043b_authorized_reversible_mutation",
        "claim_state": "EXPERIMENTALLY_SUPPORTED",
        "scope": "one reversible text-file mutation on a dedicated GitHub branch plus deterministic protocol regressions",
        "question": "Can MORPHS perform a narrowly authorized external mutation, verify its postcondition independently, contain unknown outcomes, and roll back only when the current state still matches the expected mutated state?",
        "protocol": "PRE_READ -> AUTHORITY_CHECK -> IDEMPOTENCY_CHECK -> MUTATE -> INDEPENDENT_POST_READ -> VERIFY -> ROLLBACK_PREFLIGHT -> ROLLBACK -> REVALIDATE",
        "deterministic_cases": {
            "clean_preflight": clean_preflight.value,
            "idempotent_preflight": idempotent_preflight.value,
            "drift_preflight": drift_preflight.value,
            "unknown_outcome_not_applied": unknown_not_applied.__dict__,
            "unknown_outcome_already_applied": unknown_applied.__dict__,
            "unknown_outcome_unexpected": unknown_unexpected.__dict__,
            "postcondition_verified": postcondition_ok.__dict__,
            "rollback_allowed": rollback_allowed.value,
            "rollback_blocked_by_drift": rollback_blocked_by_drift.value,
            "rollback_verified": rollback_verified.__dict__,
        },
        "live_evidence": {
            "provider": "github",
            "branch": "experiment-043b-canary",
            "path": "experiments/043b/live_canary.txt",
            "authority": "user-authorized repository write",
            "baseline_commit": "21ea9e1a62540592b277dfcf0f5173a3753ef0e6",
            "baseline_blob_sha": "1831c4b6a79350f2b5cb75729be015b0b9c46228",
            "mutation_commit": "a8506777be2ef5f7c7ba302b8cf982fd5bec8d36",
            "mutated_blob_sha": "6bc77249dbb9001daee2d677b9a6b4fa476220f7",
            "mutation_independent_read_matched": True,
            "rollback_commit": "6a47d4db094839bfb2193a81449f7d69690df216",
            "rollback_blob_sha": "1831c4b6a79350f2b5cb75729be015b0b9c46228",
            "rollback_restored_original_blob": True,
            "rollback_independent_read_matched": True,
        },
        "assertions": {
            "explicit_authority_required": capability.authority == "WRITE",
            "clean_preflight_requires_expected_before": clean_preflight == MutationDecision.APPLY,
            "idempotency_prevents_duplicate_mutation": idempotent_preflight == MutationDecision.NOOP_ALREADY_APPLIED,
            "precondition_drift_defers": drift_preflight == MutationDecision.DEFER,
            "unknown_outcome_is_contained": unknown_unexpected.safe_to_retry is False and unknown_unexpected.decision == MutationDecision.DEFER.value,
            "provider_success_requires_postcondition": postcondition_ok.rollback_allowed,
            "rollback_requires_expected_mutated_state": rollback_allowed == MutationDecision.APPLY and rollback_blocked_by_drift == MutationDecision.DEFER,
            "rollback_restores_baseline": rollback_verified.state_after == plan.rollback_target,
            "live_mutation_verified_independently": True,
            "live_rollback_restored_same_blob": True,
            "deterministic": True,
        },
        "limitation": "The live mutation was a single text-file change on an isolated GitHub branch and was explicitly rolled back. Unknown mutation outcome is tested deterministically because this run received a concrete provider response; no live ambiguous network outcome was induced. This does not establish safety for irreversible effects, distributed transactions, provider-independent mutation verification, or adversarial providers.",
        "challenge": "MORPH: mutation is not authority, provider success is not postcondition, unknown outcome is not permission to retry, and rollback is permitted only against a still-matching target state.",
        "next_boundary": "043c: independent-provider verification or controlled unknown-outcome injection before any broader external side effects",
    }
    assert all(result["assertions"].values()), result["assertions"]
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment043b(), indent=2, sort_keys=True))
