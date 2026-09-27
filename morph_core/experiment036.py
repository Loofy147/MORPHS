from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


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


@dataclass(frozen=True)
class Literal:
    field: str
    expected: object


@dataclass(frozen=True)
class ShadowVerifier:
    literals: tuple[Literal, ...]
    source_version: str

    def accept(self, evidence: Evidence) -> bool:
        return all(getattr(evidence, literal.field) == literal.expected for literal in self.literals)

    @property
    def expression(self) -> str:
        parts = []
        for literal in self.literals:
            if literal.field == "counterexamples":
                parts.append("counterexamples == 0")
            else:
                parts.append(literal.field)
        return " AND ".join(parts) if parts else "TRUE"


class ImmutableVerifierKernel:
    version = "kernel:v1"
    protected_fields = (
        "train",
        "holdout",
        "transfer",
        "adversarial",
        "intervention",
        "lineage",
        "scope",
        "negative_control",
        "counterexamples",
    )

    def accept(self, evidence: Evidence) -> bool:
        return (
            evidence.train
            and evidence.holdout
            and evidence.transfer
            and evidence.adversarial
            and evidence.intervention
            and evidence.lineage
            and evidence.scope
            and evidence.negative_control
            and evidence.counterexamples == 0
        )


class VerifierEvolutionLab:
    def __init__(self) -> None:
        self.kernel = ImmutableVerifierKernel()

    @staticmethod
    def training() -> tuple[Evidence, ...]:
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
    def holdout() -> tuple[Evidence, ...]:
        return (
            Evidence(True, True, True, True, True, True, True, True, 1),
            Evidence(True, True, True, True, True, True, True, False, 0),
            Evidence(True, True, True, True, True, True, False, True, 0),
            Evidence(True, True, True, True, True, True, True, True, 0),
        )

    @staticmethod
    def anti_gaming() -> tuple[Evidence, ...]:
        return (
            Evidence(True, True, True, False, True, True, True, True, 0),
            Evidence(True, True, True, True, True, False, True, True, 0),
            Evidence(True, True, True, True, True, True, True, False, 0),
            Evidence(True, True, True, True, True, True, True, True, 2),
        )

    @staticmethod
    def decoys() -> tuple[ShadowVerifier, ...]:
        return (
            ShadowVerifier((Literal("train", True),), "candidate:v1"),
            ShadowVerifier((Literal("train", True), Literal("holdout", True)), "candidate:v1"),
            ShadowVerifier(
                (
                    Literal("train", True),
                    Literal("holdout", True),
                    Literal("transfer", True),
                    Literal("intervention", True),
                    Literal("lineage", True),
                    Literal("scope", True),
                    Literal("negative_control", True),
                ),
                "candidate:v1",
            ),
            ShadowVerifier(
                (
                    Literal("train", True),
                    Literal("holdout", True),
                    Literal("transfer", True),
                    Literal("adversarial", True),
                    Literal("intervention", True),
                    Literal("lineage", True),
                    Literal("scope", True),
                    Literal("negative_control", True),
                    Literal("counterexamples", 1),
                ),
                "candidate:gaming",
            ),
        )

    @classmethod
    def candidate_space(cls) -> tuple[ShadowVerifier, ...]:
        fields = [
            "train",
            "holdout",
            "transfer",
            "adversarial",
            "intervention",
            "lineage",
            "scope",
            "negative_control",
            "counterexamples",
        ]
        candidates = []
        for size in range(1, len(fields) + 1):
            for subset in combinations(fields, size):
                literals = [
                    Literal(field, 0 if field == "counterexamples" else True)
                    for field in subset
                ]
                candidates.append(ShadowVerifier(tuple(literals), "candidate:search"))
        return tuple(candidates)

    def labels(self, rows: tuple[Evidence, ...]) -> tuple[bool, ...]:
        return tuple(self.kernel.accept(row) for row in rows)

    @staticmethod
    def exact_match(
        verifier: ShadowVerifier,
        rows: tuple[Evidence, ...],
        labels: tuple[bool, ...],
    ) -> bool:
        return tuple(verifier.accept(row) for row in rows) == labels

    def mutate(self) -> tuple[ShadowVerifier, tuple[Evidence, ...], tuple[bool, ...]]:
        train = self.training()
        labels = self.labels(train)
        fitting = [
            candidate
            for candidate in self.candidate_space()
            if self.exact_match(candidate, train, labels)
        ]
        if not fitting:
            raise AssertionError("no verifier candidate fits shadow training traces")
        fitting.sort(key=lambda v: (len(v.literals), v.expression))
        return fitting[0], train, labels

    def promote(self, candidate: ShadowVerifier) -> tuple[bool, dict[str, bool]]:
        holdout = self.holdout()
        anti_gaming = self.anti_gaming()
        holdout_match = self.exact_match(candidate, holdout, self.labels(holdout))
        anti_gaming_match = self.exact_match(candidate, anti_gaming, self.labels(anti_gaming))
        kernel_unchanged = self.kernel.version == "kernel:v1"
        return (
            holdout_match and anti_gaming_match and kernel_unchanged,
            {
                "candidate_holdout_match": holdout_match,
                "candidate_anti_gaming_match": anti_gaming_match,
                "kernel_unchanged": kernel_unchanged,
            },
        )

    def run(self) -> dict[str, object]:
        candidate, train, train_labels = self.mutate()
        accepted, gates = self.promote(candidate)

        decoy_results = []
        for decoy in self.decoys():
            ok, _ = self.promote(decoy)
            decoy_results.append((decoy.expression, ok))

        # Strong boundary: MORPH can propose verifier behavior, but it cannot
        # write the protected kernel or the promotion authority.
        challenge = (
            "MORPH: you may propose; you do not authorize. "
            "Pass the independent kernel or remain unpromoted."
        )

        result: dict[str, object] = {
            "experiment": "036_verifier_shadow_evolution",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic symbolic verifier-evolution simulator",
            "kernel": {
                "version": self.kernel.version,
                "protected_fields": list(self.kernel.protected_fields),
                "immutable": True,
            },
            "search": {
                "candidate_count": len(self.candidate_space()),
                "training_rows": len(train),
                "training_labels": list(train_labels),
                "promoted_candidate": candidate.expression,
                "promoted_source": candidate.source_version,
            },
            "promotion": gates | {"accepted": accepted},
            "anti_gaming": {
                "decoys_rejected": all(not ok for _, ok in decoy_results),
                "decoy_results": decoy_results,
            },
            "authority": {
                "host_kernel_retained": self.kernel.version == "kernel:v1",
                "host_controls_promotion": True,
                "host_controls_kernel": True,
                "self_authority_granted": False,
            },
            "challenge": challenge,
            "limitation": (
                "The candidate verifier is searched from a supplied conjunction grammar, "
                "and the protected kernel is supplied and immutable. 036 tests shadow "
                "verifier evolution, anti-gaming, and authority preservation; it does "
                "not establish unrestricted self-modification of verifier semantics."
            ),
        }

        result["assertions"] = {
            "candidate_found": bool(candidate.literals),
            "candidate_matches_training": self.exact_match(candidate, train, train_labels),
            "candidate_matches_holdout": gates["candidate_holdout_match"],
            "candidate_matches_anti_gaming": gates["candidate_anti_gaming_match"],
            "candidate_promoted": accepted,
            "decoys_rejected": result["anti_gaming"]["decoys_rejected"],
            "kernel_unchanged": gates["kernel_unchanged"],
            "host_controls_promotion": result["authority"]["host_controls_promotion"],
            "host_controls_kernel": result["authority"]["host_controls_kernel"],
            "self_authority_denied": not result["authority"]["self_authority_granted"],
            "deterministic": True,
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment036() -> dict[str, object]:
    return VerifierEvolutionLab().run()


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment036(), indent=2, sort_keys=True))
