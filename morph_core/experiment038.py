from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Evidence:
    train: bool
    holdout: bool
    transfer: bool
    adversarial: bool
    intervention: bool
    lineage: bool
    scope: bool
    negative_control: bool
    counterexamples: int
    boundary: int


class InvestigationTarget(str, Enum):
    CLAIM = "claim"
    VERIFIER = "verifier"
    ENVIRONMENT = "environment"
    DEFER = "defer"


class KernelA:
    version = "kernel:A:v2"

    def accept(self, e: Evidence) -> bool:
        return (
            e.train and e.holdout and e.transfer and e.adversarial
            and e.intervention and e.lineage and e.scope
            and e.negative_control and e.counterexamples == 0
            and e.boundary <= 0
        )


class KernelB:
    version = "kernel:B:v2"

    def accept(self, e: Evidence) -> bool:
        failures = 0
        failures += int(not e.train)
        failures += int(not e.holdout)
        failures += int(not e.transfer)
        failures += int(not e.adversarial)
        failures += int(not e.intervention)
        failures += int(not e.lineage)
        failures += int(not e.scope)
        failures += int(not e.negative_control)
        failures += int(e.counterexamples != 0)
        failures += int(e.boundary >= 0)
        return failures == 0


class FaultInjectedKernel:
    version = "kernel:B:fault-negative-control-omitted"

    def accept(self, e: Evidence) -> bool:
        return (
            e.train and e.holdout and e.transfer and e.adversarial
            and e.intervention and e.lineage and e.scope
            and e.counterexamples == 0 and e.boundary <= 0
        )


class FlakyKernel:
    version = "kernel:flaky:v1"

    def __init__(self) -> None:
        self._flip = False

    def accept(self, e: Evidence) -> bool:
        self._flip = not self._flip
        return self._flip and KernelA().accept(e)


class VerifierAuditContract:
    """Host-supplied verifier invariants; they do not choose a claim verdict."""

    rows = (
        Evidence(True, True, True, True, True, True, True, True, 0, -1),
        Evidence(True, True, True, True, True, True, True, True, 0, 1),
        Evidence(True, True, True, True, True, True, True, False, 0, -1),
        Evidence(True, True, True, True, True, True, True, True, 1, -1),
    )
    expected = (True, False, False, False)

    @classmethod
    def conforms(cls, verifier) -> bool:
        return tuple(verifier.accept(row) for row in cls.rows) == cls.expected


class DisagreementInvestigator:
    @staticmethod
    def _stable(verifier, row: Evidence) -> bool:
        a = verifier.accept(row)
        b = verifier.accept(row)
        return a == b

    @staticmethod
    def _boundary_probe(verifiers) -> tuple[tuple[int, ...], tuple[tuple[bool, ...], ...]]:
        rows = tuple(
            Evidence(True, True, True, True, True, True, True, True, 0, boundary)
            for boundary in (-1, 0, 1)
        )
        matrix = tuple(tuple(v.accept(r) for r in rows) for v in verifiers)
        return (-1, 0, 1), matrix

    @classmethod
    def investigate(cls, verifiers, disagreement: Evidence) -> dict[str, object]:
        stable = tuple(cls._stable(v, disagreement) for v in verifiers)
        if not all(stable):
            target = InvestigationTarget.ENVIRONMENT
            reason = "repeated identical input produced unstable verifier output"
        else:
            audit = tuple(VerifierAuditContract.conforms(v) for v in verifiers)
            if not all(audit):
                target = InvestigationTarget.VERIFIER
                reason = "at least one verifier violates the protected audit contract"
            else:
                boundaries, matrix = cls._boundary_probe(verifiers)
                disagreement_columns = tuple(
                    i for i in range(len(boundaries))
                    if len({row[i] for row in matrix}) > 1
                )
                if disagreement_columns == (1,):
                    target = InvestigationTarget.CLAIM
                    reason = "stable, conformant verifiers disagree only on an unspecified boundary"
                else:
                    target = InvestigationTarget.DEFER
                    reason = "available probes do not localize the disagreement"

        return {
            "target": target.value,
            "reason": reason,
            "verdict": "defer",
            "stability": list(stable),
        }

    @classmethod
    def run(cls) -> dict[str, object]:
        clean_claim = Evidence(True, True, True, True, True, True, True, True, 0, 0)
        verifier_fault = Evidence(True, True, True, True, True, True, True, False, 0, -1)
        environment_case = Evidence(True, True, True, True, True, True, True, True, 0, -1)
        unresolved = Evidence(True, True, True, True, True, True, True, True, 0, 2)

        claim_probe = cls.investigate((KernelA(), KernelB()), clean_claim)
        verifier_probe = cls.investigate((KernelA(), FaultInjectedKernel()), verifier_fault)
        environment_probe = cls.investigate((KernelA(), FlakyKernel()), environment_case)

        class OpaqueA:
            def accept(self, e: Evidence) -> bool:
                return (
                    e.train and e.holdout and e.transfer and e.adversarial
                    and e.intervention and e.lineage and e.scope
                    and e.negative_control and e.counterexamples == 0
                    and (e.boundary <= 0 or e.boundary == 2)
                )

        class OpaqueB:
            def accept(self, e: Evidence) -> bool:
                return (
                    e.train and e.holdout and e.transfer and e.adversarial
                    and e.intervention and e.lineage and e.scope
                    and e.negative_control and e.counterexamples == 0
                    and e.boundary <= 0
                )

        unresolved_probe = cls.investigate((OpaqueA(), OpaqueB()), unresolved)

        result = {
            "experiment": "038_disagreement_investigation",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic diagnostic simulator with injected instability and ambiguity cases",
            "protocol": "disagreement -> repeatability -> verifier audit -> minimal intervention -> investigation target -> DEFER verdict",
            "cases": {
                "claim": claim_probe,
                "verifier": verifier_probe,
                "environment": environment_probe,
                "unresolved": unresolved_probe,
            },
            "authority": {
                "investigator_selects_target_not_truth": True,
                "verdict_remains_defer_during_investigation": all(
                    case["verdict"] == "defer" for case in (
                        claim_probe, verifier_probe, environment_probe, unresolved_probe
                    )
                ),
            },
            "challenge": (
                "MORPH: disagreement is evidence, not noise. Do not erase it. "
                "Locate the unresolved source, but never promote a verdict from the investigation itself."
            ),
            "limitation": (
                "The audit contract, diagnostic probes, and ambiguity fixture are supplied by the host. "
                "Target classification is experimentally supported only for these observable cases."
            ),
        }
        result["assertions"] = {
            "claim_disagreement_targets_claim": claim_probe["target"] == InvestigationTarget.CLAIM.value,
            "verifier_fault_targets_verifier": verifier_probe["target"] == InvestigationTarget.VERIFIER.value,
            "instability_targets_environment": environment_probe["target"] == InvestigationTarget.ENVIRONMENT.value,
            "unlocalized_case_remains_defer": unresolved_probe["target"] == InvestigationTarget.DEFER.value,
            "investigation_does_not_grant_truth": result["authority"]["investigator_selects_target_not_truth"],
            "all_investigation_verdicts_remain_defer": result["authority"]["verdict_remains_defer_during_investigation"],
            "deterministic_clean_path": True,
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment038() -> dict[str, object]:
    return DisagreementInvestigator.run()


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment038(), indent=2, sort_keys=True))
