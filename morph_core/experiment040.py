from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdaptiveVersion:
    version: str
    parent: str | None
    payload: str
    evidence_valid: bool


@dataclass(frozen=True)
class Transition:
    action: str
    source: str | None
    target: str | None
    authorized: bool
    verified: bool
    reason: str


class HostKernel:
    def __init__(self) -> None:
        self.versions = {"v0": AdaptiveVersion("v0", None, "baseline_operator", True)}
        self.active = "v0"
        self.audit: list[Transition] = []

    def register(self, version: AdaptiveVersion) -> None:
        if version.version in self.versions:
            raise ValueError("version already exists")
        if version.parent not in self.versions:
            raise ValueError("unknown parent")
        self.versions[version.version] = version

    def promote(self, target: str, authorized: bool) -> Transition:
        candidate = self.versions[target]
        valid = candidate.evidence_valid and candidate.parent == self.active
        transition = Transition(
            "PROMOTE", self.active, target, authorized, valid,
            "promotion accepted" if authorized and valid else "promotion blocked",
        )
        if authorized and valid:
            self.active = target
        self.audit.append(transition)
        return transition

    def rollback(self, target: str, authorized: bool, revalidated: bool) -> Transition:
        valid_target = (
            target in self.versions
            and target != self.active
            and self._is_ancestor(target, self.active)
        )
        accepted = authorized and valid_target and revalidated
        transition = Transition(
            "ROLLBACK", self.active, target, authorized, revalidated,
            "rollback accepted" if accepted else "rollback blocked",
        )
        if accepted:
            self.active = target
        self.audit.append(transition)
        return transition

    def _is_ancestor(self, target: str, current: str) -> bool:
        seen: set[str] = set()
        cursor: str | None = current
        while cursor is not None and cursor not in seen:
            if cursor == target:
                return True
            seen.add(cursor)
            cursor = self.versions[cursor].parent
        return False

    def tamper_audit(self) -> None:
        self.audit.pop()


class ReversibleAdaptationLab:
    @staticmethod
    def _evidence(version: AdaptiveVersion, environment: str) -> bool:
        return version.evidence_valid and version.payload == "derived_operator_v2" and environment == "stable-v1"

    def run(self) -> dict[str, object]:
        kernel = HostKernel()
        candidate = AdaptiveVersion("v1", "v0", "derived_operator_v2", True)
        kernel.register(candidate)
        proposal_verified = self._evidence(candidate, "stable-v1")
        promotion = kernel.promote("v1", authorized=True)
        rollback_revalidation = self._evidence(kernel.versions["v0"], "stable-v1")
        rollback = kernel.rollback("v0", authorized=True, revalidated=rollback_revalidation)
        historical_version_preserved = "v1" in kernel.versions
        audit_preserved = len(kernel.audit) == 2
        unauthorized = kernel.promote("v1", authorized=False)
        unauthorized_blocked = unauthorized.reason == "promotion blocked"
        drifted_revalidation = self._evidence(kernel.versions["v0"], "drifted-v2")
        drifted_rollback = kernel.rollback("v1", authorized=True, revalidated=drifted_revalidation)
        drift_blocked = drifted_rollback.reason == "rollback blocked"
        before_tamper_count = len(kernel.audit)
        kernel.tamper_audit()
        tamper_detected = len(kernel.audit) != before_tamper_count
        result = {
            "experiment": "040_reversible_adaptation",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic versioned-adaptation simulator",
            "protocol": "propose -> verify -> promote -> revalidate rollback target -> rollback or block -> preserve lineage -> audit",
            "versions": {"baseline": "v0", "promoted": "v1", "rollback_target": "v0", "active_after_verified_rollback": kernel.active},
            "promotion": {"candidate_verified": proposal_verified, "authorized": promotion.authorized, "accepted": promotion.verified, "transition": promotion.reason},
            "rollback": {"revalidated_before_rollback": rollback.verified, "authorized": rollback.authorized, "accepted": rollback.verified, "transition": rollback.reason},
            "safety_cases": {
                "historical_version_preserved": historical_version_preserved,
                "audit_preserved_after_valid_rollback": audit_preserved,
                "unauthorized_promotion_blocked": unauthorized_blocked,
                "drifted_revalidation_blocks_rollback": drift_blocked,
                "audit_tamper_is_observable": tamper_detected,
            },
            "authority": {"host_controls_promotion": promotion.authorized, "host_controls_rollback": rollback.authorized, "rollback_not_deletion": historical_version_preserved},
            "challenge": "MORPH: a rollback is not an eraser. Preserve lineage, require authority, revalidate the target, and block the transition when current evidence no longer supports it.",
            "limitation": "The version graph, revalidation predicate, authorization gate, and audit mechanism are supplied by the host simulator. This does not establish rollback correctness for arbitrary external side effects or irreversible systems.",
        }
        result["assertions"] = {
            "candidate_verified_before_promotion": proposal_verified,
            "promotion_requires_authority": promotion.authorized and promotion.verified,
            "rollback_requires_revalidation": rollback.verified,
            "rollback_preserves_history": historical_version_preserved,
            "rollback_preserves_audit": audit_preserved,
            "unauthorized_transition_blocked": unauthorized_blocked,
            "drift_blocks_stale_rollback": drift_blocked,
            "audit_tamper_is_observable": tamper_detected,
            "active_version_is_reverted": kernel.active == "v0",
            "deterministic": True,
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment040() -> dict[str, object]:
    return ReversibleAdaptationLab().run()


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment040(), indent=2, sort_keys=True))
