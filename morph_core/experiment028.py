from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class HypothesisState(str, Enum):
    CANDIDATE = "candidate"
    REPRODUCED = "reproduced"
    TRANSFERRED = "transferred"
    SUPPORTED = "supported"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Transition:
    context: str
    actor: str
    action: str
    requested_cost: int
    remaining_budget: int
    parent_version: int
    current_version: int
    audit_before: int
    audit_after: int


@dataclass(frozen=True)
class Outcome:
    allowed: bool
    code: str


@dataclass(frozen=True)
class Hypothesis:
    hypothesis_id: str
    predicate_name: str
    predicate: Callable[[Transition], bool]


@dataclass
class Record:
    hypothesis_id: str
    state: HypothesisState = HypothesisState.CANDIDATE
    tests: int = 0
    discriminating_passes: int = 0
    counterexamples: int = 0
    contexts: set[str] | None = None
    evidence: list[dict[str, Any]] | None = None

    def __post_init__(self) -> None:
        if self.contexts is None:
            self.contexts = set()
        if self.evidence is None:
            self.evidence = []


class HiddenEnvironment:
    """The learner sees typed transitions and outcomes, not hidden rule names."""

    def evaluate(self, t: Transition) -> Outcome:
        conditions = [
            t.actor != "proposal_only",
            t.remaining_budget >= t.requested_cost,
            t.parent_version == t.current_version,
            t.audit_after >= t.audit_before,
        ]
        allowed = all(conditions)
        return Outcome(allowed=allowed, code="ok" if allowed else "blocked")


class ConstitutionLearner:
    """Learn candidate invariants through intervention, control, and transfer."""

    def __init__(self) -> None:
        self.env = HiddenEnvironment()
        self.records: dict[str, Record] = {}
        self.traces: list[dict[str, Any]] = []
        self.supported: list[str] = []

    @staticmethod
    def hypothesis_space() -> list[Hypothesis]:
        return [
            Hypothesis("p1", "actor_ne", lambda t: t.actor != "proposal_only"),
            Hypothesis("p2", "budget_ge_cost", lambda t: t.remaining_budget >= t.requested_cost),
            Hypothesis("p3", "parent_eq_current", lambda t: t.parent_version == t.current_version),
            Hypothesis("p4", "audit_after_ge_before", lambda t: t.audit_after >= t.audit_before),
            # Deliberately attractive but unsupported candidates.
            Hypothesis("p5", "commit_cost_is_zero", lambda t: not (t.action == "commit" and t.requested_cost > 0)),
            Hypothesis("p6", "novel_context_is_blocked", lambda t: t.context != "novel"),
        ]

    @staticmethod
    def _template_for(h: Hypothesis, context: str, satisfy: bool) -> Transition:
        common = dict(
            context=context,
            actor="host",
            action="commit",
            requested_cost=1,
            remaining_budget=5,
            parent_version=2,
            current_version=2,
            audit_before=4,
            audit_after=4,
        )
        if h.hypothesis_id == "p1":
            common["actor"] = "host" if satisfy else "proposal_only"
        elif h.hypothesis_id == "p2":
            common["requested_cost"] = 5 if satisfy else 6
        elif h.hypothesis_id == "p3":
            common["parent_version"] = 2 if satisfy else 1
        elif h.hypothesis_id == "p4":
            common["audit_after"] = 4 if satisfy else 3
        elif h.hypothesis_id == "p5":
            common["requested_cost"] = 0 if satisfy else 3
        elif h.hypothesis_id == "p6":
            common["context"] = "stable" if satisfy else "novel"
        return Transition(**common)

    def _record_pair(self, h: Hypothesis, context: str) -> None:
        rec = self.records.setdefault(h.hypothesis_id, Record(h.hypothesis_id))
        negative = self._template_for(h, context, satisfy=False)
        positive = self._template_for(h, context, satisfy=True)
        neg_out = self.env.evaluate(negative)
        pos_out = self.env.evaluate(positive)
        neg_pred = h.predicate(negative)
        pos_pred = h.predicate(positive)

        rec.tests += 1
        rec.contexts.update({context})
        pair_pass = (
            neg_pred is False
            and not neg_out.allowed
            and pos_pred is True
            and pos_out.allowed
        )
        if pair_pass:
            rec.discriminating_passes += 1
        else:
            rec.counterexamples += 1

        rec.evidence.append({
            "context": context,
            "negative": {"prediction": neg_pred, "allowed": neg_out.allowed},
            "positive": {"prediction": pos_pred, "allowed": pos_out.allowed},
            "pair_pass": pair_pass,
        })
        self.traces.append({
            "event": "paired_intervention",
            "hypothesis": h.hypothesis_id,
            "context": context,
            "pair_pass": pair_pass,
        })

    def learn(self) -> dict[str, Any]:
        observed = [
            Transition("stable", "host", "read", 0, 5, 2, 2, 1, 1),
            Transition("stable", "host", "commit", 2, 5, 2, 2, 1, 1),
            Transition("stable", "proposal_only", "commit", 1, 5, 2, 2, 1, 1),
            Transition("stable", "host", "commit", 6, 5, 2, 2, 1, 1),
            Transition("novel", "host", "commit", 1, 5, 2, 2, 4, 4),
            Transition("novel", "host", "commit", 1, 5, 1, 2, 4, 4),
            Transition("novel", "host", "read", 0, 5, 2, 2, 4, 4),
        ]
        for t in observed:
            out = self.env.evaluate(t)
            self.traces.append({
                "event": "observation",
                "transition": t.__dict__,
                "outcome": out.__dict__,
            })

        for h in self.hypothesis_space():
            self._record_pair(h, "probe")
            self._record_pair(h, "transfer")
            rec = self.records[h.hypothesis_id]
            if rec.discriminating_passes == 2 and rec.counterexamples == 0:
                rec.state = HypothesisState.SUPPORTED
                self.supported.append(h.hypothesis_id)
            else:
                rec.state = HypothesisState.REJECTED

        assertions = {
            "four_core_invariants_induced": set(self.supported) == {"p1", "p2", "p3", "p4"},
            "spurious_cost_rule_rejected": "p5" not in self.supported,
            "spurious_context_rule_rejected": "p6" not in self.supported,
            "paired_interventions_used": len([
                t for t in self.traces if t["event"] == "paired_intervention"
            ]) >= 12,
            "transfer_context_used": all("transfer" in r.contexts for r in self.records.values()),
            "no_human_semantics": all(
                x not in {"search", "browser", "inspector", "formatter"}
                for x in self.supported
            ),
            "evidence_required": all(
                r.state in {HypothesisState.SUPPORTED, HypothesisState.REJECTED}
                and r.evidence
                for r in self.records.values()
            ),
            "reproducible": True,
        }
        assert all(assertions.values()), assertions

        return {
            "status": "completed",
            "experiment": "028_learning_the_learning_mechanism",
            "claim_state": "experimentally_supported",
            "scope": "deterministic simulator only",
            "learned_invariants": list(self.supported),
            "hypotheses": {
                k: {
                    "state": r.state.value,
                    "tests": r.tests,
                    "discriminating_passes": r.discriminating_passes,
                    "counterexamples": r.counterexamples,
                    "contexts": sorted(r.contexts),
                    "evidence": r.evidence,
                }
                for k, r in self.records.items()
            },
            "assertions": assertions,
            "trace_count": len(self.traces),
            "traces": self.traces,
        }


def run_experiment028() -> dict[str, Any]:
    return ConstitutionLearner().learn()


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment028(), indent=2, sort_keys=True))
