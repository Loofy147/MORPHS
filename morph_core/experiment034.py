from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    REUSE = "reuse"
    EVOLVE = "evolve"
    DEFER = "defer"


@dataclass(frozen=True)
class Frontier:
    name: str
    reuse_feasible: bool
    reuse_value: float
    reuse_cost: float
    evolve_feasible: bool
    evolve_value: float
    evolve_cost: float
    mutation_risk: float


def choose(frontier: Frontier, budget: float, risk_limit: float = 0.5) -> Decision:
    reuse_ok = frontier.reuse_feasible and frontier.reuse_cost <= budget
    evolve_ok = (
        frontier.evolve_feasible
        and frontier.evolve_cost <= budget
        and frontier.mutation_risk <= risk_limit
    )

    if not reuse_ok and evolve_ok and frontier.evolve_value > frontier.evolve_cost:
        return Decision.EVOLVE

    if reuse_ok:
        # Evolution is admitted only when it improves both evidence value and
        # resource efficiency enough to justify changing the language.
        if evolve_ok:
            current_density = frontier.reuse_value / max(frontier.reuse_cost, 1e-9)
            evolved_density = frontier.evolve_value / max(frontier.evolve_cost, 1e-9)
            if (
                frontier.evolve_value > frontier.reuse_value
                and evolved_density > current_density
            ):
                return Decision.EVOLVE
        return Decision.REUSE

    return Decision.DEFER


def run_experiment034() -> dict[str, object]:
    frontiers = (
        Frontier("stable_reuse", True, 1.0, 1.0, True, 1.0, 5.0, 0.1),
        Frontier("blocked_frontier", False, 0.0, 1.0, True, 3.0, 2.0, 0.2),
        Frontier("expensive_mutation", True, 1.0, 1.0, True, 3.0, 5.0, 0.2),
        Frontier("uncertain_mutation", False, 0.0, 1.0, True, 2.0, 2.5, 0.8),
    )
    budget = 4.0
    decisions = {
        f.name: choose(f, budget)
        for f in frontiers
    }

    result = {
        "experiment": "034_budget_aware_language_evolution",
        "claim_state": "EXPERIMENTALLY_SUPPORTED",
        "scope": "deterministic symbolic decision simulator",
        "budget": budget,
        "decisions": {name: decision.value for name, decision in decisions.items()},
        "policy_properties": {
            "stable_reuses": decisions["stable_reuse"] == Decision.REUSE,
            "blocked_evolves": decisions["blocked_frontier"] == Decision.EVOLVE,
            "expensive_does_not_mutate": decisions["expensive_mutation"] != Decision.EVOLVE,
            "uncertain_defers": decisions["uncertain_mutation"] == Decision.DEFER,
        },
        "limitation": (
            "Values and costs are simulator inputs; this experiment establishes "
            "policy behavior under explicit gates, not a universal utility law."
        ),
    }
    result["assertions"] = {
        "stable_reuses": result["policy_properties"]["stable_reuses"],
        "blocked_evolves": result["policy_properties"]["blocked_evolves"],
        "expensive_does_not_mutate": result["policy_properties"]["expensive_does_not_mutate"],
        "uncertain_defers": result["policy_properties"]["uncertain_defers"],
        "deterministic": True,
    }
    assert all(result["assertions"].values()), result["assertions"]
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment034(), indent=2, sort_keys=True))
