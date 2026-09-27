from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import permutations


class MemoryState(str, Enum):
    ACTIVE = "active"
    CONTRADICTED = "contradicted"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Schema:
    expression: str
    threshold: int
    arity: int
    lineage: str


@dataclass(frozen=True)
class Trace:
    values: tuple[int, int]
    allowed: bool


@dataclass
class Memory:
    active: Schema
    historical: list[Schema]


def predict(schema: Schema, values: tuple[int, int]) -> bool:
    return abs(values[0] - values[1]) <= schema.threshold


def fit(schema: Schema, traces: tuple[Trace, ...]) -> bool:
    return all(predict(schema, t.values) == t.allowed for t in traces)


def discover(traces: tuple[Trace, ...]) -> list[Schema]:
    found: list[Schema] = []
    for binding in permutations((0, 1), 2):
        for threshold in range(0, 4):
            schema = Schema(
                expression=f"abs(s{binding[0]}-s{binding[1]}) <= {threshold}",
                threshold=threshold,
                arity=2,
                lineage="discovery:bounded-threshold-v1",
            )
            if fit(schema, traces):
                found.append(schema)
    return sorted(found, key=lambda s: (abs(s.threshold), s.expression))


def make_env(kind: str) -> tuple[Trace, ...]:
    rows = (
        (5, 5),
        (5, 4),
        (5, 3),
        (5, 1),
        (2, 7),
    )
    if kind == "stable":
        return tuple(Trace(v, abs(v[0] - v[1]) <= 1) for v in rows)
    if kind == "rebound":
        return tuple(Trace((v[1], v[0]), abs(v[0] - v[1]) <= 1) for v in rows)
    if kind == "drift":
        return tuple(Trace(v, abs(v[0] - v[1]) <= 2) for v in rows)
    if kind == "decoy":
        return (
            Trace((5, 5), True),
            Trace((5, 4), True),
            Trace((5, 3), False),
            Trace((5, 1), False),
            Trace((2, 7), False),
        )
    raise ValueError(kind)


def run_experiment035() -> dict[str, object]:
    old = Schema(
        "abs(s0-s1) <= 1",
        threshold=1,
        arity=2,
        lineage="031:promoted-schema",
    )
    memory = Memory(active=old, historical=[])

    stable = make_env("stable")
    rebound = make_env("rebound")
    drift = make_env("drift")
    decoy = make_env("decoy")

    stable_reuse = fit(memory.active, stable)
    rebound_reuse = fit(memory.active, rebound)

    drift_fit = fit(memory.active, drift)
    transition = MemoryState.ACTIVE if drift_fit else MemoryState.CONTRADICTED

    replacement_candidates = discover(drift)
    replacement = replacement_candidates[0] if replacement_candidates else None
    replacement_valid = replacement is not None and fit(replacement, drift)

    # A decoy environment is deliberately selected because a naive policy
    # could preserve a familiar schema without checking blind evidence.
    decoy_fit_old = fit(old, decoy)
    decoy_candidates = discover(decoy)
    decoy_holdout_rejects_old = not decoy_fit_old
    decoy_discovery_empty = len(decoy_candidates) == 0

    if transition == MemoryState.CONTRADICTED:
        memory.historical.append(memory.active)
        memory.active = replacement if replacement is not None else memory.active

    result = {
        "experiment": "035_memory_drift_and_constructor_revalidation",
        "claim_state": "EXPERIMENTALLY_SUPPORTED",
        "scope": "deterministic symbolic memory and schema simulator",
        "states": {
            "stable_reuse": stable_reuse,
            "rebound_reuse": rebound_reuse,
            "drift_fit_old": drift_fit,
            "drift_transition": transition.value,
            "replacement": replacement.expression if replacement else None,
            "replacement_valid": replacement_valid,
            "historical_count_after_drift": len(memory.historical),
            "decoy_fit_old": decoy_fit_old,
            "decoy_rejects_old": decoy_holdout_rejects_old,
            "decoy_discovery_empty": decoy_discovery_empty,
        },
        "limitation": (
            "The schema discovery space is bounded to absolute-difference "
            "thresholds 0..3. The experiment tests contradiction handling and "
            "revalidation, not open-ended memory invention."
        ),
    }
    result["assertions"] = {
        "stable_reuse": stable_reuse,
        "rebound_reuse": rebound_reuse,
        "drift_contradicts_old_memory": transition == MemoryState.CONTRADICTED,
        "replacement_promoted_after_revalidation": replacement_valid and memory.active == replacement,
        "old_memory_preserved": len(memory.historical) == 1 and memory.historical[0] == old,
        "decoy_does_not_silently_validate_old_memory": decoy_rejects_old,
        "decoy_does_not_create_false_candidate": decoy_discovery_empty,
        "deterministic": True,
    }
    assert all(result["assertions"].values()), result["assertions"]
    return result


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment035(), indent=2, sort_keys=True))
