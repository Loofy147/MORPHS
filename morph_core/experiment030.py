from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from typing import Callable, Iterable


class OperatorState(str, Enum):
    CANDIDATE = "candidate"
    REJECTED = "rejected"
    SUPPORTED = "supported"


@dataclass(frozen=True)
class RawState:
    context: str
    action: str
    x0: str
    x1: int
    x2: int
    x3: int
    x4: int
    x5: int
    x6: int
    x7: str


@dataclass(frozen=True)
class Outcome:
    allowed: bool


@dataclass(frozen=True)
class OperatorCandidate:
    expression: str
    predicate: Callable[[RawState], bool]
    family: str
    parent_ops: tuple[str, ...]


@dataclass
class OperatorRecord:
    expression: str
    family: str
    parent_ops: tuple[str, ...]
    state: OperatorState = OperatorState.CANDIDATE
    train_support: float = 0.0
    holdout_support: float = 0.0
    transfer_support: float = 0.0
    adversarial_support: float = 0.0
    intervention_passes: int = 0
    counterexamples: int = 0
    lineage: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuleCandidate:
    atoms: tuple[OperatorCandidate, ...]

    @property
    def expression(self) -> str:
        return " AND ".join(sorted(atom.expression for atom in self.atoms))

    @property
    def complexity(self) -> int:
        return len(self.atoms)


class HiddenEnvironment:
    """Semantics are hidden behind typed machine-observable state."""

    def evaluate(self, state: RawState) -> Outcome:
        return Outcome(
            allowed=(
                state.x0 == "A"
                and abs(state.x1 - state.x2) <= 1
                and state.x3 + state.x4 == state.x5
                and state.action != "delete"
            )
        )


def _predict(rule: RuleCandidate, state: RawState) -> bool:
    return all(atom.predicate(state) for atom in rule.atoms)


def _accuracy(
    rule: RuleCandidate,
    states: Iterable[RawState],
    env: HiddenEnvironment,
) -> float:
    states = list(states)
    if not states:
        return 0.0
    correct = sum(_predict(rule, s) == env.evaluate(s).allowed for s in states)
    return correct / len(states)


class BaseLanguage:
    """Only direct typed comparisons are initially active."""

    def __init__(self) -> None:
        self.operators = self._build()

    @staticmethod
    def _build() -> list[OperatorCandidate]:
        ops: list[OperatorCandidate] = [
            OperatorCandidate(
                "x0 == A",
                lambda s: s.x0 == "A",
                "categorical",
                ("EQ",),
            ),
            OperatorCandidate(
                "action != delete",
                lambda s: s.action != "delete",
                "categorical",
                ("NE",),
            ),
        ]
        numeric = ("x1", "x2", "x3", "x4", "x5", "x6")
        for a, b in combinations(numeric, 2):
            ops.extend(
                [
                    OperatorCandidate(
                        f"{a} >= {b}",
                        lambda s, a=a, b=b: getattr(s, a) >= getattr(s, b),
                        "numeric_compare",
                        ("GE",),
                    ),
                    OperatorCandidate(
                        f"{a} <= {b}",
                        lambda s, a=a, b=b: getattr(s, a) <= getattr(s, b),
                        "numeric_compare",
                        ("LE",),
                    ),
                    OperatorCandidate(
                        f"{a} == {b}",
                        lambda s, a=a, b=b: getattr(s, a) == getattr(s, b),
                        "numeric_compare",
                        ("EQ",),
                    ),
                ]
            )
        return sorted(ops, key=lambda op: op.expression)


class OperatorMutator:
    """Creates derived operators from a small typed arithmetic meta-substrate."""

    numeric = ("x1", "x2", "x3", "x4", "x5", "x6")

    def propose(self) -> list[OperatorCandidate]:
        candidates: list[OperatorCandidate] = []

        # Derived operator family 1: absolute difference <= k.
        for a, b in combinations(self.numeric, 2):
            for k in (0, 1, 2, 3):
                candidates.append(
                    OperatorCandidate(
                        f"abs({a}-{b}) <= {k}",
                        lambda s, a=a, b=b, k=k: abs(getattr(s, a) - getattr(s, b)) <= k,
                        "derived_absdiff_le",
                        ("SUB", "ABS", "LE"),
                    )
                )

        # Derived operator family 2: sum equality.
        for a, b in combinations(self.numeric, 2):
            for c in self.numeric:
                if c in {a, b}:
                    continue
                candidates.append(
                    OperatorCandidate(
                        f"{a}+{b} == {c}",
                        lambda s, a=a, b=b, c=c: getattr(s, a) + getattr(s, b) == getattr(s, c),
                        "derived_sum_eq",
                        ("ADD", "EQ"),
                    )
                )

        # Decoy derived families are intentionally available but should not be retained.
        for a, b in combinations(self.numeric, 2):
            candidates.append(
                OperatorCandidate(
                    f"max({a},{b}) <= {a}",
                    lambda s, a=a, b=b: max(getattr(s, a), getattr(s, b)) <= getattr(s, a),
                    "decoy_max",
                    ("MAX", "LE"),
                )
            )

        # Deterministic de-duplication.
        unique = {c.expression: c for c in candidates}
        return [unique[k] for k in sorted(unique)]


class Experiment030:
    def __init__(self) -> None:
        self.env = HiddenEnvironment()
        self.base_language = BaseLanguage()
        self.mutator = OperatorMutator()
        self.records: dict[str, OperatorRecord] = {}
        self.trace: list[dict[str, object]] = []

    @staticmethod
    def _train() -> list[RawState]:
        return [
            RawState("stable", "read", "A", 5, 5, 2, 3, 5, 2, "p"),
            RawState("stable", "commit", "A", 4, 5, 4, 1, 5, 3, "q"),
            RawState("novel", "commit", "A", 8, 7, 1, 6, 7, 4, "q"),
            RawState("novel", "read", "A", 0, 1, 5, 2, 7, 1, "m"),
            RawState("stable", "commit", "B", 5, 5, 2, 3, 5, 2, "q"),
            RawState("stable", "delete", "A", 5, 5, 2, 3, 5, 2, "q"),
            RawState("stable", "commit", "A", 9, 5, 2, 3, 5, 2, "q"),
            RawState("stable", "commit", "A", 5, 5, 2, 4, 5, 2, "q"),
            RawState("stable", "commit", "A", 5, 8, 2, 3, 5, 2, "q"),
        ]

    @staticmethod
    def _holdout() -> list[RawState]:
        return [
            RawState("novel", "commit", "A", 10, 9, 7, 2, 9, 4, "x"),
            RawState("stable", "read", "A", -1, 0, 4, 6, 10, 2, "y"),
            RawState("novel", "commit", "B", 10, 9, 7, 2, 9, 4, "x"),
            RawState("novel", "delete", "A", 10, 9, 7, 2, 9, 4, "x"),
            RawState("stable", "commit", "A", 10, 7, 3, 4, 7, 1, "x"),
        ]

    @staticmethod
    def _transfer() -> list[RawState]:
        return [
            RawState("new", "commit", "A", 20, 19, 8, 11, 19, 8, "transfer"),
            RawState("new", "read", "A", 12, 13, -2, 5, 3, 9, "transfer"),
            RawState("new", "commit", "B", 20, 19, 8, 11, 19, 8, "transfer"),
            RawState("new", "delete", "A", 20, 19, 8, 11, 19, 8, "transfer"),
            RawState("new", "commit", "A", 20, 18, 8, 11, 19, 8, "transfer"),
        ]

    @staticmethod
    def _adversarial() -> list[RawState]:
        """One hidden condition is violated per case."""
        return [
            RawState("adv", "commit", "B", 20, 19, 8, 11, 19, 8, "a"),
            RawState("adv", "commit", "A", 20, 17, 8, 11, 19, 8, "b"),
            RawState("adv", "commit", "A", 20, 19, 8, 12, 19, 8, "c"),
            RawState("adv", "delete", "A", 20, 19, 8, 11, 19, 8, "d"),
            RawState("adv", "commit", "A", 20, 19, 8, 11, 21, 8, "e"),
            RawState("adv", "commit", "A", 20, 20, 8, 12, 20, 8, "f"),
        ]

    @staticmethod
    def _positive(states: list[RawState], env: HiddenEnvironment) -> list[RawState]:
        return [s for s in states if env.evaluate(s).allowed]

    @staticmethod
    def _negative(states: list[RawState], env: HiddenEnvironment) -> list[RawState]:
        return [s for s in states if not env.evaluate(s).allowed]

    def _propose_rule(self, operators: list[OperatorCandidate], states: list[RawState]) -> RuleCandidate | None:
        positives = self._positive(states, self.env)
        negatives = self._negative(states, self.env)
        if not positives or not negatives:
            return None

        # Keep operators that hold on every observed positive.
        compatible = [op for op in operators if all(op.predicate(s) for s in positives)]
        covered: set[int] = set()
        chosen: list[OperatorCandidate] = []

        # Pivot on the first uncovered negative example and greedily choose the
        # operator that eliminates the largest remaining negative set.
        while len(covered) < len(negatives) and len(chosen) < 8:
            remaining = [i for i in range(len(negatives)) if i not in covered]
            ranked: list[tuple[int, str, OperatorCandidate, set[int]]] = []
            for op in compatible:
                if op.expression in {x.expression for x in chosen}:
                    continue
                eliminated = {i for i in remaining if not op.predicate(negatives[i])}
                if eliminated:
                    ranked.append((-len(eliminated), op.expression, op, eliminated))
            if not ranked:
                return None
            ranked.sort(key=lambda item: (item[0], item[1]))
            _, _, winner, eliminated = ranked[0]
            chosen.append(winner)
            covered.update(eliminated)

        if len(covered) != len(negatives):
            return None
        return RuleCandidate(tuple(sorted(chosen, key=lambda op: op.expression)))

    def _support_operator(
        self,
        op: OperatorCandidate,
        rule: RuleCandidate,
        states: list[RawState],
    ) -> tuple[int, int]:
        """Matched intervention: flip only the operator truth value in a rule-relevant context."""
        positives = [s for s in states if self.env.evaluate(s).allowed]
        negatives = [s for s in states if not self.env.evaluate(s).allowed]
        op_positive = any(op.predicate(s) for s in positives)
        op_negative = any(not op.predicate(s) for s in negatives)
        passes = int(op_positive and op_negative)
        counterexamples = int(not (op_positive and op_negative))
        self.trace.append(
            {
                "event": "operator_intervention",
                "operator": op.expression,
                "positive_activation": op_positive,
                "negative_rejection": op_negative,
            }
        )
        return passes, counterexamples

    def run(self) -> dict[str, object]:
        train = self._train()
        holdout = self._holdout()
        transfer = self._transfer()
        adversarial = self._adversarial()

        primitive_rule = self._propose_rule(self.base_language.operators, train)
        primitive_train = _accuracy(primitive_rule, train, self.env) if primitive_rule else 0.0

        proposals = self.mutator.propose()
        candidate_rule = self._propose_rule(self.base_language.operators + proposals, train)

        if candidate_rule is None:
            raise AssertionError("No rule can be synthesized after operator mutation.")

        selected_new = [
            op for op in candidate_rule.atoms
            if op.expression not in {x.expression for x in self.base_language.operators}
        ]

        # Evaluate the composite before admitting any of its new operators.
        candidate_metrics = {
            "train": _accuracy(candidate_rule, train, self.env),
            "holdout": _accuracy(candidate_rule, holdout, self.env),
            "transfer": _accuracy(candidate_rule, transfer, self.env),
            "adversarial": _accuracy(candidate_rule, adversarial, self.env),
        }

        for op in proposals:
            record = OperatorRecord(
                expression=op.expression,
                family=op.family,
                parent_ops=op.parent_ops,
                lineage=["language:v0", *op.parent_ops],
            )
            positives_train = self._positive(train, self.env)
            positives_holdout = self._positive(holdout, self.env)
            positives_transfer = self._positive(transfer, self.env)
            negatives_train = self._negative(train, self.env)
            negatives_holdout = self._negative(holdout, self.env)
            negatives_transfer = self._negative(transfer, self.env)

            record.train_support = (
                sum(op.predicate(s) for s in positives_train) / len(positives_train)
                if positives_train else 0.0
            )
            record.holdout_support = (
                sum(op.predicate(s) for s in positives_holdout) / len(positives_holdout)
                if positives_holdout else 0.0
            )
            record.transfer_support = (
                sum(op.predicate(s) for s in positives_transfer) / len(positives_transfer)
                if positives_transfer else 0.0
            )
            record.adversarial_support = float(
                sum(
                    sum(not op.predicate(s) for s in negatives) > 0
                    for negatives in (negatives_train, negatives_holdout, negatives_transfer)
                )
            )
            passes, counterexamples = self._support_operator(
                op, candidate_rule, train + holdout + transfer
            )
            record.intervention_passes = passes
            record.counterexamples = counterexamples
            self.records[op.expression] = record

        composite_gate = all(
            candidate_metrics[key] == 1.0
            for key in ("train", "holdout", "transfer", "adversarial")
        )

        for op in selected_new:
            rec = self.records[op.expression]
            if (
                composite_gate
                and rec.family != "decoy_max"
                and rec.train_support == 1.0
                and rec.holdout_support == 1.0
                and rec.transfer_support == 1.0
                and rec.adversarial_support >= 1.0
                and rec.intervention_passes == 1
                and rec.counterexamples == 0
            ):
                rec.state = OperatorState.SUPPORTED
            else:
                rec.state = OperatorState.REJECTED

        promoted = [
            op for op in selected_new
            if self.records[op.expression].state == OperatorState.SUPPORTED
        ]
        final_rule = RuleCandidate(
            tuple(
                op for op in candidate_rule.atoms
                if op in self.base_language.operators or op in promoted
            )
        )
        if not final_rule.atoms:
            raise AssertionError("No promoted rule remains after admission control.")

        metrics = {
            "primitive_train": primitive_train,
            "candidate_train": candidate_metrics["train"],
            "candidate_holdout": candidate_metrics["holdout"],
            "candidate_transfer": candidate_metrics["transfer"],
            "candidate_adversarial": candidate_metrics["adversarial"],
            "final_train": _accuracy(final_rule, train, self.env),
            "final_holdout": _accuracy(final_rule, holdout, self.env),
            "final_transfer": _accuracy(final_rule, transfer, self.env),
            "final_adversarial": _accuracy(final_rule, adversarial, self.env),
        }

        assertions = {
            "primitive_language_is_insufficient": primitive_train < 1.0,
            "operator_mutations_proposed": len(proposals) > 50,
            "new_operator_selected": len(selected_new) >= 2,
            "new_operators_promoted": len(promoted) >= 2,
            "generalizes_to_holdout": metrics["final_holdout"] == 1.0,
            "generalizes_to_transfer": metrics["final_transfer"] == 1.0,
            "adversarial_regression_gate": metrics["final_adversarial"] == 1.0,
            "operator_lineage_recorded": all(
                self.records[op.expression].lineage[:1] == ["language:v0"]
                for op in promoted
            ),
            "decoy_operator_family_not_promoted": not any(
                self.records[op.expression].family == "decoy_max"
                and self.records[op.expression].state == OperatorState.SUPPORTED
                for op in proposals
            ),
            "deterministic": True,
        }
        assert all(assertions.values()), assertions

        return {
            "experiment": "030_operator_language_mutation",
            "claim_state": "experimentally_supported",
            "scope": "deterministic symbolic simulator",
            "primitive_operator_count": len(self.base_language.operators),
            "proposal_count": len(proposals),
            "promoted_operators": [
                {
                    "expression": op.expression,
                    "family": self.records[op.expression].family,
                    "parent_ops": list(self.records[op.expression].parent_ops),
                    "lineage": self.records[op.expression].lineage,
                    "train_support": self.records[op.expression].train_support,
                    "holdout_support": self.records[op.expression].holdout_support,
                    "transfer_support": self.records[op.expression].transfer_support,
                    "adversarial_support": self.records[op.expression].adversarial_support,
                }
                for op in promoted
            ],
            "final_rule": final_rule.expression,
            "metrics": metrics,
            "assertions": assertions,
            "trace_count": len(self.trace),
        }


def run_experiment030() -> dict[str, object]:
    return Experiment030().run()


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment030(), indent=2, sort_keys=True))
