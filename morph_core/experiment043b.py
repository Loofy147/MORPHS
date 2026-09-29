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


@dataclass(frozen=True)
class MutationCapability:
    capability_id: str
    provider: str
    operation: str
    authority: str
    side_effects: tuple[str, ...]
    verification_paths: tuple[str, ...]
    identity_scope: str


@dataclass(frozen=True)
class MutationAuthorization:
    granted: bool
    authority_source: str
    capability_id: str
    scope: str
    allowed_side_effects: tuple[str, ...]


@dataclass(frozen=True)
class MutationPlan:
    expected_before_state: str
    expected_before_blob_sha: str
    desired_after_state: str
    desired_after_blob_sha: str
    rollback_target_state: str
    rollback_target_blob_sha: str


@dataclass(frozen=True)
class MutationObservation:
    state: str
    blob_sha: str


@dataclass(frozen=True)
class ProtocolResult:
    decision: str
    outcome: str
    state_after: str
    blob_sha_after: str
    safe_to_retry: bool
    rollback_allowed: bool
    reason: str


class ReversibleMutationProtocol:
    def __init__(self, capability: MutationCapability) -> None:
        self.capability = capability

    def validate(self, authorization: MutationAuthorization) -> None:
        if self.capability.authority != "WRITE":
            raise ValueError("043b requires explicit write capability")
        if not authorization.granted:
            raise PermissionError("043b mutation is not authorized")
        if authorization.capability_id != self.capability.capability_id:
            raise PermissionError("043b authorization is not bound to the capability")
        if authorization.scope != self.capability.identity_scope:
            raise PermissionError("043b authorization scope does not match the capability")
        if not set(self.capability.side_effects).issubset(
            set(authorization.allowed_side_effects)
        ):
            raise PermissionError("043b requested side effects exceed authorization")
        if "INDEPENDENT_READ" not in self.capability.verification_paths:
            raise ValueError("043b requires an independent read path")
        if "ROLLBACK_READ" not in self.capability.verification_paths:
            raise ValueError("043b requires rollback revalidation")

    @staticmethod
    def matches(
        observation: MutationObservation,
        state: str,
        blob_sha: str,
    ) -> bool:
        return observation.state == state and observation.blob_sha == blob_sha

    def preflight(
        self,
        current: MutationObservation,
        plan: MutationPlan,
        authorization: MutationAuthorization,
    ) -> MutationDecision:
        self.validate(authorization)
        if self.matches(
            current,
            plan.desired_after_state,
            plan.desired_after_blob_sha,
        ):
            return MutationDecision.NOOP_ALREADY_APPLIED
        if not self.matches(
            current,
            plan.expected_before_state,
            plan.expected_before_blob_sha,
        ):
            return MutationDecision.DEFER
        return MutationDecision.APPLY

    @classmethod
    def classify_unknown(
        cls,
        observed_after_unknown: MutationObservation,
        plan: MutationPlan,
    ) -> ProtocolResult:
        if cls.matches(
            observed_after_unknown,
            plan.desired_after_state,
            plan.desired_after_blob_sha,
        ):
            return ProtocolResult(
                MutationDecision.NOOP_ALREADY_APPLIED.value,
                OutcomeClass.APPLIED.value,
                observed_after_unknown.state,
                observed_after_unknown.blob_sha,
                False,
                False,
                "unknown provider outcome resolved by observation: already applied",
            )
        if cls.matches(
            observed_after_unknown,
            plan.expected_before_state,
            plan.expected_before_blob_sha,
        ):
            return ProtocolResult(
                MutationDecision.APPLY.value,
                OutcomeClass.NOT_APPLIED.value,
                observed_after_unknown.state,
                observed_after_unknown.blob_sha,
                True,
                False,
                "unknown provider outcome resolved by observation: not applied",
            )
        return ProtocolResult(
            MutationDecision.DEFER.value,
            OutcomeClass.PARTIAL.value,
            observed_after_unknown.state,
            observed_after_unknown.blob_sha,
            False,
            False,
            "unknown provider outcome resolved to unexpected state or identity; contain and investigate",
        )

    @classmethod
    def verify_postcondition(
        cls,
        observed_after: MutationObservation,
        plan: MutationPlan,
    ) -> ProtocolResult:
        if not cls.matches(
            observed_after,
            plan.desired_after_state,
            plan.desired_after_blob_sha,
        ):
            return ProtocolResult(
                MutationDecision.DEFER.value,
                OutcomeClass.PARTIAL.value,
                observed_after.state,
                observed_after.blob_sha,
                False,
                False,
                "independent postcondition failed: state or content identity mismatch",
            )
        return ProtocolResult(
            MutationDecision.NOOP_ALREADY_APPLIED.value,
            OutcomeClass.APPLIED.value,
            observed_after.state,
            observed_after.blob_sha,
            False,
            True,
            "independent postcondition verified",
        )

    @classmethod
    def rollback_preflight(
        cls,
        current: MutationObservation,
        plan: MutationPlan,
    ) -> MutationDecision:
        if not cls.matches(
            current,
            plan.desired_after_state,
            plan.desired_after_blob_sha,
        ):
            return MutationDecision.DEFER
        return MutationDecision.APPLY

    @classmethod
    def verify_rollback(
        cls,
        observed_after_rollback: MutationObservation,
        plan: MutationPlan,
    ) -> ProtocolResult:
        if not cls.matches(
            observed_after_rollback,
            plan.rollback_target_state,
            plan.rollback_target_blob_sha,
        ):
            return ProtocolResult(
                MutationDecision.DEFER.value,
                OutcomeClass.PARTIAL.value,
                observed_after_rollback.state,
                observed_after_rollback.blob_sha,
                False,
                False,
                "rollback postcondition failed: state or content identity mismatch",
            )
        return ProtocolResult(
            MutationDecision.NOOP_ALREADY_APPLIED.value,
            OutcomeClass.APPLIED.value,
            observed_after_rollback.state,
            observed_after_rollback.blob_sha,
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
        identity_scope="experiment-043b-canary:experiments/043b/live_canary.txt",
    )
    authorization = MutationAuthorization(
        granted=True,
        authority_source="host_authorization_fixture",
        capability_id=capability.capability_id,
        scope=capability.identity_scope,
        allowed_side_effects=("REPOSITORY_FILE_MUTATION",),
    )
    protocol = ReversibleMutationProtocol(capability)
    plan = MutationPlan(
        expected_before_state="baseline",
        expected_before_blob_sha="baseline-blob",
        desired_after_state="mutated",
        desired_after_blob_sha="mutated-blob",
        rollback_target_state="baseline",
        rollback_target_blob_sha="baseline-blob",
    )

    clean_preflight = protocol.preflight(
        MutationObservation("baseline", "baseline-blob"),
        plan,
        authorization,
    )
    idempotent_preflight = protocol.preflight(
        MutationObservation("mutated", "mutated-blob"),
        plan,
        authorization,
    )
    wrong_identity_preflight = protocol.preflight(
        MutationObservation("mutated", "unexpected-blob"),
        plan,
        authorization,
    )
    drift_preflight = protocol.preflight(
        MutationObservation("drifted", "drifted-blob"),
        plan,
        authorization,
    )

    unknown_not_applied = protocol.classify_unknown(
        MutationObservation("baseline", "baseline-blob"),
        plan,
    )
    unknown_applied = protocol.classify_unknown(
        MutationObservation("mutated", "mutated-blob"),
        plan,
    )
    unknown_wrong_identity = protocol.classify_unknown(
        MutationObservation("mutated", "unexpected-blob"),
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
    postcondition_wrong_identity = protocol.verify_postcondition(
        MutationObservation("mutated", "unexpected-blob"),
        plan,
    )
    rollback_allowed = protocol.rollback_preflight(
        MutationObservation("mutated", "mutated-blob"),
        plan,
    )
    rollback_blocked_by_state_drift = protocol.rollback_preflight(
        MutationObservation("drifted", "drifted-blob"),
        plan,
    )
    rollback_blocked_by_identity_drift = protocol.rollback_preflight(
        MutationObservation("mutated", "newer-blob"),
        plan,
    )
    rollback_verified = protocol.verify_rollback(
        MutationObservation("baseline", "baseline-blob"),
        plan,
    )
    rollback_wrong_identity = protocol.verify_rollback(
        MutationObservation("baseline", "unexpected-blob"),
        plan,
    )

    mismatched_authorization = MutationAuthorization(
        granted=True,
        authority_source="wrong_scope",
        capability_id="other.capability",
        scope="other-resource",
        allowed_side_effects=("REPOSITORY_FILE_MUTATION",),
    )
    unauthorized_rejected = False
    try:
        protocol.preflight(
            MutationObservation("baseline", "baseline-blob"),
            plan,
            mismatched_authorization,
        )
    except PermissionError:
        unauthorized_rejected = True

    live_runtime_integration = "OPEN"

    result = {
        "experiment": "043b_authorized_reversible_mutation",
        "claim_state": "EXPERIMENTALLY_SUPPORTED",
        "scope": "deterministic reversible-mutation protocol model; host-captured live canary evidence recorded separately",
        "runtime_integration": {
            "status": live_runtime_integration,
            "reason": "run_experiment043b does not invoke GitHub. The live canary mutation was executed by host-side GitHub tooling and is not used as runtime evidence by this module.",
        },
        "question": "Can the mutation protocol require exact pre-state identity, bound authorization, idempotency, independent postcondition, unknown-outcome containment, and rollback revalidation?",
        "protocol": "PRE_READ -> AUTHORITY_CHECK -> IDEMPOTENCY_CHECK -> MUTATE -> INDEPENDENT_POST_READ -> VERIFY -> ROLLBACK_PREFLIGHT -> ROLLBACK -> REVALIDATE",
        "deterministic_cases": {
            "clean_preflight": clean_preflight.value,
            "idempotent_preflight": idempotent_preflight.value,
            "wrong_identity_preflight": wrong_identity_preflight.value,
            "drift_preflight": drift_preflight.value,
            "unknown_outcome_not_applied": unknown_not_applied.__dict__,
            "unknown_outcome_already_applied": unknown_applied.__dict__,
            "unknown_outcome_wrong_identity": unknown_wrong_identity.__dict__,
            "unknown_outcome_unexpected": unknown_unexpected.__dict__,
            "postcondition_verified": postcondition_ok.__dict__,
            "postcondition_wrong_identity": postcondition_wrong_identity.__dict__,
            "rollback_allowed": rollback_allowed.value,
            "rollback_blocked_by_state_drift": rollback_blocked_by_state_drift.value,
            "rollback_blocked_by_identity_drift": rollback_blocked_by_identity_drift.value,
            "rollback_verified": rollback_verified.__dict__,
            "rollback_wrong_identity": rollback_wrong_identity.__dict__,
            "mismatched_authorization_rejected": unauthorized_rejected,
        },
        "assertions": {
            "clean_preflight_requires_exact_expected_identity": clean_preflight == MutationDecision.APPLY,
            "idempotency_requires_state_and_identity": idempotent_preflight == MutationDecision.NOOP_ALREADY_APPLIED
            and wrong_identity_preflight == MutationDecision.DEFER,
            "unknown_outcome_requires_exact_identity": (
                unknown_applied.outcome == OutcomeClass.APPLIED.value
                and unknown_not_applied.outcome == OutcomeClass.NOT_APPLIED.value
                and unknown_wrong_identity.decision == MutationDecision.DEFER.value
                and unknown_unexpected.safe_to_retry is False
            ),
            "postcondition_requires_state_and_identity": (
                postcondition_ok.rollback_allowed
                and postcondition_wrong_identity.decision == MutationDecision.DEFER.value
            ),
            "rollback_requires_exact_mutated_identity": (
                rollback_allowed == MutationDecision.APPLY
                and rollback_blocked_by_state_drift == MutationDecision.DEFER
                and rollback_blocked_by_identity_drift == MutationDecision.DEFER
            ),
            "rollback_revalidation_requires_exact_target_identity": (
                rollback_verified.outcome == OutcomeClass.APPLIED.value
                and rollback_wrong_identity.decision == MutationDecision.DEFER.value
            ),
            "authorization_is_bound_to_capability_and_scope": unauthorized_rejected,
            "runtime_integration_is_not_overclaimed": live_runtime_integration == "OPEN",
            "deterministic": True,
        },
        "limitation": "This module verifies protocol semantics only. The live GitHub canary is separate host-captured evidence. It does not establish MORPHS runtime integration, provider-independent verification, real ambiguous outcomes, distributed transaction semantics, or irreversible-effect safety.",
        "next_boundary": "043c: provider-independent verification or controlled unknown-outcome injection at the provider-adapter boundary",
    }
    assert all(result["assertions"].values()), result["assertions"]
    return result


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment043b(), indent=2, sort_keys=True))
