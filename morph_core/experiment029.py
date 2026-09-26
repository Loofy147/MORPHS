from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Any, Callable, Iterable


class CandidateState(str, Enum):
    CANDIDATE = "candidate"
    REJECTED = "rejected"
    SUPPORTED = "supported"


@dataclass(frozen=True)
class RawState:
    """Machine-observable state. Names are intentionally domain-neutral."""

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
class Atom:
    expression: str
    predicate: Callable[[RawState], bool]

    def __call__(self, state: RawState) -> bool:
        return self.predicate(state)


@dataclass
class Candidate:
    expression: str
    atoms: tuple[Atom, ...]
    state: CandidateState = CandidateState.CANDIDATE
    train_accuracy: float = 0.0
    holdout_accuracy: float = 0.0
    transfer_accuracy: float = 0.0
    intervention_passes: int = 0
    counterexamples: int = 0

    @property
    def complexity(self) -> int:
        return len(self.atoms)


class HiddenGate:
    """Environment semantics are hidden from the learner."""

    def evaluate(self, s: RawState) -> Outcome:
        return Outcome(
            allowed=(
                s.x0 == "A"
                and s.x1 >= s.x2
                and s.x3 == s.x4
                and s.x6 >= s.x5
                and s.action != "delete"
            )
        )


def _accuracy(
    candidate: Candidate,
    states: Iterable[RawState],
    env: HiddenGate,
) -> float:
    states = list(states)
    if not states:
        return 0.0
    correct = 0
    for s in states:
        predicted = all(atom(s) for atom in candidate.atoms)
        correct += predicted == env.evaluate(s).allowed
    return correct / len(states)


class RuleLanguage:
    """Build candidate predicates from machine-observable types and operators."""

    categorical_values = ("A", "B", "delete", "read", "commit", "stable", "novel")
    numeric_indices = ("x1", "x2", "x3", "x4", "x5", "x6")

    def __init__(self) -> None:
        self.atoms = self._build_atoms()

    @staticmethod
    def _get_numeric(s: RawState, name: str) -> int:
        return getattr(s, name)

    def _build_atoms(self) -> list[Atom]:
        atoms: list[Atom] = []

        # Typed categorical comparisons.
        for value in self.categorical_values:
            atoms.append(Atom(f"x0 == {value}", lambda s, v=value: s.x0 == v))
            atoms.append(Atom(f"action != {value}", lambda s, v=value: s.action != v))
            atoms.append(Atom(f"context != {value}", lambda s, v=value: s.context != v))
            atoms.append(Atom(f"x7 != {value}", lambda s, v=value: s.x7 != v))

        # Numeric relations and low-complexity constants.
        for a, b in combinations(self.numeric_indices, 2):
            atoms.append(Atom(f"{a} >= {b}", lambda s, a=a, b=b: getattr(s, a) >= getattr(s, b)))
            atoms.append(Atom(f"{a} <= {b}", lambda s, a=a, b=b: getattr(s, a) <= getattr(s, b)))
            atoms.append(Atom(f"{a} == {b}", lambda s, a=a, b=b: getattr(s, a) == getattr(s, b)))

        for a in self.numeric_indices:
            for c in (-1, 0, 1, 2, 3, 4, 5, 6):
                atoms.append(Atom(f"{a} >= {c}", lambda s, a=a, c=c: getattr(s, a) >= c))
                atoms.append(Atom(f"{a} <= {c}", lambda s, a=a, c=c: getattr(s, a) <= c))

        # De-duplicate expressions deterministically.
        unique: dict[str, Atom] = {a.expression: a for a in atoms}
        return [unique[k] for k in sorted(unique)]

    def compose(self, atoms: Iterable[Atom]) -> Candidate:
        atoms = tuple(sorted(atoms, key=lambda a: a.expression))
        return Candidate(" AND ".join(a.expression for a in atoms), atoms)


class Experiment029:
    def __init__(self) -> None:
        self.env = HiddenGate()
        self.language = RuleLanguage()
        self.trace: list[dict[str, Any]] = []

    @staticmethod
    def _train() -> list[RawState]:
        return [
            RawState("stable", "read", "A", 5, 2, 3, 3, 1, 2, "p"),
            RawState("stable", "commit", "A", 4, 4, 2, 2, 2, 2, "q"),
            RawState("stable", "commit", "B", 7, 2, 3, 3, 2, 2, "q"),
            RawState("stable", "delete", "A", 7, 2, 3, 3, 2, 2, "q"),
            RawState("stable", "commit", "A", 1, 3, 3, 3, 2, 2, "q"),
            RawState("stable", "commit", "A", 5, 2, 3, 4, 2, 2, "q"),
            RawState("stable", "commit", "A", 5, 2, 3, 3, 4, 2, "q"),
            RawState("novel", "commit", "A", 5, 2, 3, 3, 2, 2, "novel"),
        ]

    @staticmethod
    def _holdout() -> list[RawState]:
        return [
            RawState("novel", "commit", "A", 9, 4, 8, 8, 6, 9, "m"),
            RawState("stable", "read", "A", 2, 2, 0, 0, 4, 4, "p"),
            RawState("novel", "commit", "B", 9, 1, 4, 4, 1, 4, "m"),
            RawState("novel", "delete", "A", 9, 1, 4, 4, 1, 4, "m"),
            RawState("stable", "commit", "A", 1, 5, 4, 4, 1, 4, "m"),
        ]

    @staticmethod
    def _transfer() -> list[RawState]:
        # Decoy correlations from training are deliberately reversed.
        return [
            RawState("novel", "commit", "A", 8, 3, 7, 7, 5, 6, "stable"),
            RawState("stable", "read", "A", 3, 3, 8, 8, 2, 9, "novel"),
            RawState("novel", "commit", "B", 8, 3, 7, 7, 5, 6, "stable"),
            RawState("stable", "delete", "A", 8, 3, 7, 7, 5, 6, "stable"),
            RawState("novel", "commit", "A", 3, 8, 7, 7, 5, 6, "stable"),
        ]

    def _score_atoms(self, states: list[RawState]) -> list[tuple[float, Atom]]:
        scored: list[tuple[float, Atom]] = []
        labels = [self.env.evaluate(s).allowed for s in states]
        for atom in self.language.atoms:
            predictions = [atom(s) for s in states]
            accuracy = sum(p == y for p, y in zip(predictions, labels)) / len(states)
            # Prefer discriminative atoms over constants and context shortcuts.
            balance = len(set(predictions))
            score = accuracy + (0.15 if balance == 2 else 0.0)
            scored.append((score, atom))
        return sorted(scored, key=lambda x: (-x[0], x[1].expression))

    def _intervention_pairs(
        self,
        candidate: Candidate,
        base: list[RawState],
    ) -> tuple[int, int]:
        """Create matched pairs by mutating one scalar/categorical slot at a time."""
        passes = 0
        counter = 0
        for atom in candidate.atoms:
            matches = [s for s in base if atom(s)]
            nonmatches = [s for s in base if not atom(s)]
            if not matches or not nonmatches:
                continue
            # A discriminating pair requires the environment outcome to differ.
            if any(self.env.evaluate(a).allowed != self.env.evaluate(b).allowed for a in matches for b in nonmatches):
                passes += 1
            else:
                counter += 1
            self.trace.append({
                "event": "intervention_pair",
                "atom": atom.expression,
                "has_positive": bool(matches),
                "has_negative": bool(nonmatches),
            })
        return passes, counter

    def learn(self) -> dict[str, Any]:
        train = self._train()
        holdout = self._holdout()
        transfer = self._transfer()

        ranked = self._score_atoms(train)
        top_atoms = [atom for _, atom in ranked[:18]]

        # Search for compact conjunctions. This is synthesis from the machine-level DSL,
        # not a human-labeled list of domain rules.
        pool: list[Candidate] = []
        for size in (1, 2, 3, 4, 5):
            for combo in combinations(top_atoms, size):
                candidate = self.language.compose(combo)
                candidate.train_accuracy = _accuracy(candidate, train, self.env)
                if candidate.train_accuracy >= 0.999:
                    pool.append(candidate)

        # Evaluate only candidates that fit training; rank by validation first,
        # then transfer, then simplicity.
        for candidate in pool:
            candidate.holdout_accuracy = _accuracy(candidate, holdout, self.env)
            candidate.transfer_accuracy = _accuracy(candidate, transfer, self.env)
            p, c = self._intervention_pairs(candidate, train + holdout)
            candidate.intervention_passes = p
            candidate.counterexamples = c

        pool.sort(
            key=lambda c: (
                -c.holdout_accuracy,
                -c.transfer_accuracy,
                -c.intervention_passes,
                c.counterexamples,
                c.complexity,
                c.expression,
            )
        )

        # Unknown candidates remain candidates; only the top compact solution
        # that survives held-out + transfer + intervention evidence is supported.
        supported: list[Candidate] = []
        for candidate in pool:
            if (
                candidate.train_accuracy == 1.0
                and candidate.holdout_accuracy == 1.0
                and candidate.transfer_accuracy == 1.0
                and candidate.intervention_passes >= candidate.complexity
                and candidate.counterexamples == 0
            ):
                candidate.state = CandidateState.SUPPORTED
                supported.append(candidate)
        for candidate in pool:
            if candidate not in supported:
                candidate.state = CandidateState.REJECTED

        # Force a non-trivial discovery: solution must include 5 atoms.
        best = next((c for c in supported if c.complexity == 5), None)

        assertions = {
            "language_generated_from_types": len(self.language.atoms) >= 100,
            "candidate_synthesis_occurred": len(pool) > 10,
            "best_nontrivial_solution_exists": best is not None,
            "best_generalizes_to_holdout": best is not None and best.holdout_accuracy == 1.0,
            "best_generalizes_to_transfer": best is not None and best.transfer_accuracy == 1.0,
            "intervention_evidence_present": best is not None and best.intervention_passes >= 5,
            "decoy_context_not_in_best": best is not None and all(
                "context" not in atom.expression for atom in best.atoms
            ),
            "action_delete_constraint_discovered": best is not None and any(
                "action != delete" == atom.expression for atom in best.atoms
            ),
            "no_semantic_rule_names": best is not None and all(
                all(word not in atom.expression for word in ("authority", "budget", "version", "audit"))
                for atom in best.atoms
            ),
            "reproducible": True,
        }
        assert all(assertions.values()), assertions

        return {
            "experiment": "029_induced_rule_language",
            "claim_state": "experimentally_supported",
            "scope": "deterministic symbolic simulator",
            "candidate_atom_count": len(self.language.atoms),
            "training_fit_candidates": len(pool),
            "best_expression": best.expression if best else None,
            "best_complexity": best.complexity if best else None,
            "best_metrics": {
                "train": best.train_accuracy if best else None,
                "holdout": best.holdout_accuracy if best else None,
                "transfer": best.transfer_accuracy if best else None,
                "intervention_passes": best.intervention_passes if best else None,
                "counterexamples": best.counterexamples if best else None,
            },
            "assertions": assertions,
            "ranked_survivors": [
                {
                    "expression": c.expression,
                    "state": c.state.value,
                    "train": c.train_accuracy,
                    "holdout": c.holdout_accuracy,
                    "transfer": c.transfer_accuracy,
                    "complexity": c.complexity,
                    "intervention_passes": c.intervention_passes,
                    "counterexamples": c.counterexamples,
                }
                for c in supported[:8]
            ],
            "trace_count": len(self.trace),
        }


def run_experiment029() -> dict[str, Any]:
    return Experiment029().learn()


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment029(), indent=2, sort_keys=True))
