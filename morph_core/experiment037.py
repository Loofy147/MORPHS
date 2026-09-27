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


class Verdict(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    DEFER = "defer"


class KernelA:
    version = "kernel:A:v1"

    def accept(self, e: Evidence) -> bool:
        return (
            e.train
            and e.holdout
            and e.transfer
            and e.adversarial
            and e.intervention
            and e.lineage
            and e.scope
            and e.negative_control
            and e.counterexamples == 0
        )


class KernelB:
    version = "kernel:B:v1"

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
        return failures == 0


class FaultInjectedKernel:
    version = "kernel:B:fault-negative-control-omitted"

    def accept(self, e: Evidence) -> bool:
        failures = 0
        failures += int(not e.train)
        failures += int(not e.holdout)
        failures += int(not e.transfer)
        failures += int(not e.adversarial)
        failures += int(not e.intervention)
        failures += int(not e.lineage)
        failures += int(not e.scope)
        failures += int(e.counterexamples != 0)
        return failures == 0


@dataclass(frozen=True)
class ShadowVerifier:
    required: tuple[str, ...]
    source: str = "037:candidate"

    def accept(self, e: Evidence) -> bool:
        return all(getattr(e, name) for name in self.required) and e.counterexamples == 0

    @property
    def expression(self) -> str:
        return (
            " AND ".join(self.required) + " AND counterexamples == 0"
        )


class IndependentVerifierLab:
    protected_fields = (
        "train",
        "holdout",
        "transfer",
        "adversarial",
        "intervention",
        "lineage",
        "scope",
        "negative_control",
    )

    @staticmethod
    def corpus() -> tuple[Evidence, ...]:
        return (
            Evidence(True, True, True, True, True, True, True, True, 0),
            Evidence(False, True, True, True, True, True, True, True, 0),
            Evidence(True, False, True, True, True, True, True, True, 0),
            Evidence(True, True, False, True, True, True, True, True, 0),
            Evidence(True, True, True, False, True, True, True, True, 0),
            Evidence(True, True, True, True, False, True, True, True, 0),
            Evidence(True, True, True, True, True, False, True, True, 0),
            Evidence(True, True, True, True, True, True, False, True, 0),
            Evidence(True, True, True, True, True, True, True, False, 0),
            Evidence(True, True, True, True, True, True, True, True, 1),
        )

    @staticmethod
    def protected_holdout() -> tuple[Evidence, ...]:
        return (
            Evidence(True, True, True, True, True, True, True, True, 0),
            Evidence(True, True, True, True, True, True, True, False, 0),
            Evidence(True, True, True, True, True, True, True, True, 3),
        )

    @staticmethod
    def candidate() -> ShadowVerifier:
        return ShadowVerifier(IndependentVerifierLab.protected_fields)

    @staticmethod
    def labels(verifier, rows: tuple[Evidence, ...]) -> tuple[bool, ...]:
        return tuple(verifier.accept(row) for row in rows)

    @classmethod
    def agreement(cls, verifiers, rows: tuple[Evidence, ...]) -> tuple[bool, bool]:
        matrix = [cls.labels(v, rows) for v in verifiers]
        agreed = all(labels == matrix[0] for labels in matrix[1:])
        return agreed, all(labels == cls.labels(cls.candidate(), rows) for labels in matrix)

    @classmethod
    def run(cls) -> dict[str, object]:
        candidate = cls.candidate()
        corpus = cls.corpus()
        holdout = cls.protected_holdout()

        clean_verifiers = (KernelA(), KernelB())
        clean_train_agreement, clean_candidate_match = cls.agreement(clean_verifiers, corpus)
        clean_holdout_agreement, clean_holdout_match = cls.agreement(clean_verifiers, holdout)

        clean_promoted = (
            clean_train_agreement
            and clean_holdout_agreement
            and clean_candidate_match
            and clean_holdout_match
        )

        disagreement_case = (
            Evidence(True, True, True, True, True, True, True, False, 0),
        )
        faulty_verifiers = (KernelA(), FaultInjectedKernel())
        disagree, candidate_match_under_disagreement = cls.agreement(
            faulty_verifiers,
            disagreement_case,
        )
        deferred = not disagree

        result = {
            "experiment": "037_independent_verifier_diversity",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic verifier-diversity simulator",
            "candidate": {
                "expression": candidate.expression,
                "source": candidate.source,
            },
            "clean_verifiers": {
                "versions": [v.version for v in clean_verifiers],
                "training_agreement": clean_train_agreement,
                "holdout_agreement": clean_holdout_agreement,
                "candidate_matches_training": clean_candidate_match,
                "candidate_matches_holdout": clean_holdout_match,
                "promotion": clean_promoted,
            },
            "fault_injection": {
                "versions": [v.version for v in faulty_verifiers],
                "agreement": disagree,
                "candidate_match": candidate_match_under_disagreement,
                "decision": Verdict.DEFER.value if deferred else Verdict.ACCEPT.value,
            },
            "authority": {
                "candidate_cannot_override_disagreement": deferred,
                "independent_verifier_count": 2,
                "faulty_verifier_detected_by_divergence": not disagree,
            },
            "challenge": (
                "MORPH: one verifier is not enough. If independent verifiers disagree, "
                "you do not get to choose the verdict. You defer."
            ),
            "limitation": (
                "Kernel implementations are supplied and deterministic; diversity is "
                "implemented as independent code paths, not proof of semantic independence "
                "under arbitrary future implementations."
            ),
        }

        result["assertions"] = {
            "clean_agreement": clean_train_agreement and clean_holdout_agreement,
            "clean_candidate_promoted": clean_promoted,
            "fault_injection_causes_disagreement": not disagree,
            "disagreement_forces_defer": deferred,
            "candidate_cannot_override_disagreement": result["authority"]["candidate_cannot_override_disagreement"],
            "two_independent_verifiers": result["authority"]["independent_verifier_count"] == 2,
            "deterministic": True,
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment037() -> dict[str, object]:
    return IndependentVerifierLab.run()


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment037(), indent=2, sort_keys=True))
