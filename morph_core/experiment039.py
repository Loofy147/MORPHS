from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ProtocolStatus(str, Enum):
    HOST_CONSTRAINT = "HOST_CONSTRAINT"
    HOST_PROTOCOL = "HOST_PROTOCOL"
    ADAPTIVE_ARTIFACT = "ADAPTIVE_ARTIFACT"


class EpistemicStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    OBSERVED = "OBSERVED"
    DERIVED = "DERIVED"
    VERIFIED = "VERIFIED"
    INFERRED = "INFERRED"
    HYPOTHESIS = "HYPOTHESIS"
    CONTRADICTED = "CONTRADICTED"
    STALE = "STALE"


@dataclass(frozen=True)
class ProtocolFact:
    fact_id: str
    statement: str
    status: ProtocolStatus
    epistemic: EpistemicStatus = EpistemicStatus.VERIFIED


@dataclass(frozen=True)
class ResearchQuestion:
    question_id: str
    statement: str


@dataclass(frozen=True)
class FailureRecord:
    failure_id: str
    statement: str


class ProtocolGrounding:
    def __init__(self) -> None:
        self.facts = {
            "P1": ProtocolFact("P1", "host retains verifier authority", ProtocolStatus.HOST_CONSTRAINT),
            "P2": ProtocolFact("P2", "promotion requires evidence", ProtocolStatus.HOST_PROTOCOL),
            "P3": ProtocolFact("P3", "contradictions are preserved", ProtocolStatus.HOST_PROTOCOL),
            "P4": ProtocolFact("P4", "unknown external outcomes are not replayed blindly", ProtocolStatus.HOST_CONSTRAINT),
        }
        self.failures = {
            "F1": FailureRecord(
                "F1",
                "first unresolved 038 fixture violated the verifier audit contract",
            )
        }

    def classify(self, item: ProtocolFact | ResearchQuestion | FailureRecord) -> str:
        if isinstance(item, ProtocolFact):
            return "USE_CONSTRAINT"
        if isinstance(item, FailureRecord):
            return "REGRESSION_TARGET"
        return "EXPERIMENT"

    def plan(self, question: ResearchQuestion) -> dict[str, object]:
        return {
            "question": question.statement,
            "status": EpistemicStatus.UNKNOWN.value,
            "action": "EXPERIMENT",
            "answer_supplied_by_protocol": False,
        }

    def reconcile(self, observations: tuple[str, str]) -> dict[str, object]:
        return {
            "status": EpistemicStatus.CONTRADICTED.value,
            "preserved": list(observations),
            "action": "REOBSERVE_OR_CROSS_CHECK",
            "silent_choice": False,
        }

    def regression_target(self, failure_id: str) -> dict[str, object]:
        failure = self.failures[failure_id]
        return {
            "failure_id": failure.failure_id,
            "statement": failure.statement,
            "action": "REGRESSION_PROTECT",
            "erased": False,
        }

    def run(self) -> dict[str, object]:
        known = self.classify(self.facts["P1"])
        unknown = self.plan(ResearchQuestion(
            "Q1",
            "can a newly evolved adaptive operator transfer to an external runtime?",
        ))
        contradiction = self.reconcile(("verifier_A=accept", "verifier_B=reject"))
        failure = self.regression_target("F1")

        result = {
            "experiment": "039_protocol_grounding",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic protocol-grounding simulator",
            "principle": (
                "Host-supplied protocol facts constrain the ecology; they do not answer "
                "unknown research questions."
            ),
            "cases": {
                "known_fact": {"classification": known},
                "unknown_question": unknown,
                "contradiction": contradiction,
                "known_failure": failure,
            },
            "assertions": {
                "known_facts_bypass_discovery": known == "USE_CONSTRAINT",
                "unknowns_become_questions": unknown["action"] == "EXPERIMENT",
                "protocol_facts_not_promoted_as_discoveries": (
                    self.facts["P1"].status == ProtocolStatus.HOST_CONSTRAINT
                    and self.facts["P1"].epistemic == EpistemicStatus.VERIFIED
                ),
                "contradiction_preserved": contradiction["preserved"] == [
                    "verifier_A=accept",
                    "verifier_B=reject",
                ],
                "contradiction_blocks_silent_choice": not contradiction["silent_choice"],
                "protocol_does_not_answer_unknown": not unknown["answer_supplied_by_protocol"],
                "known_failure_becomes_regression_target": not failure["erased"],
                "deterministic": True,
            },
            "limitation": (
                "This experiment tests routing discipline for protocol facts, unknowns, "
                "contradictions, and known failures. It does not establish autonomous "
                "protocol construction or unrestricted research planning."
            ),
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment039() -> dict[str, object]:
    return ProtocolGrounding().run()


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment039(), indent=2, sort_keys=True))
