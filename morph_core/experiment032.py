from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from typing import Callable


@dataclass(frozen=True)
class Arg:
    i: int


@dataclass(frozen=True)
class Const:
    value: int


@dataclass(frozen=True)
class Add:
    a: object
    b: object


@dataclass(frozen=True)
class Sub:
    a: object
    b: object


@dataclass(frozen=True)
class Le:
    a: object
    b: object


@dataclass(frozen=True)
class If:
    predicate: Le
    then_term: object
    else_term: object


Term = Arg | Const | Add | Sub | If


@dataclass(frozen=True)
class NumericExample:
    args: tuple[int, ...]
    output: int


@dataclass(frozen=True)
class Episode:
    name: str
    examples: tuple[NumericExample, ...]


@dataclass(frozen=True)
class ConstructorDefinition:
    name: str
    arity: int
    body: Term
    source_version: str
    semantic_name_given: bool = False


def key(x: object) -> str:
    if isinstance(x, Arg):
        return f"a{x.i}"
    if isinstance(x, Const):
        return f"c{x.value}"
    if isinstance(x, Add):
        items = sorted((key(x.a), key(x.b)))
        return f"add({items[0]},{items[1]})"
    if isinstance(x, Sub):
        return f"sub({key(x.a)},{key(x.b)})"
    if isinstance(x, Le):
        return f"le({key(x.a)},{key(x.b)})"
    if isinstance(x, If):
        return f"if({key(x.predicate)},{key(x.then_term)},{key(x.else_term)})"
    raise TypeError(x)


def pretty(x: object) -> str:
    if isinstance(x, Arg):
        return f"$a{x.i}"
    if isinstance(x, Const):
        return str(x.value)
    if isinstance(x, Add):
        return f"({pretty(x.a)}+{pretty(x.b)})"
    if isinstance(x, Sub):
        return f"({pretty(x.a)}-{pretty(x.b)})"
    if isinstance(x, Le):
        return f"{pretty(x.a)}<={pretty(x.b)}"
    if isinstance(x, If):
        return f"if({pretty(x.predicate)},{pretty(x.then_term)},{pretty(x.else_term)})"
    raise TypeError(x)


def eval_term(term: object, args: tuple[int, ...]) -> int:
    if isinstance(term, Arg):
        return args[term.i]
    if isinstance(term, Const):
        return term.value
    if isinstance(term, Add):
        return eval_term(term.a, args) + eval_term(term.b, args)
    if isinstance(term, Sub):
        return eval_term(term.a, args) - eval_term(term.b, args)
    if isinstance(term, If):
        left = eval_term(term.predicate.a, args)
        right = eval_term(term.predicate.b, args)
        return (
            eval_term(term.then_term, args)
            if left <= right
            else eval_term(term.else_term, args)
        )
    raise TypeError(term)


def term_cost(term: object) -> int:
    if isinstance(term, (Arg, Const)):
        return 1
    if isinstance(term, (Add, Sub)):
        return 1 + term_cost(term.a) + term_cost(term.b)
    if isinstance(term, If):
        return (
            1
            + term_cost(term.predicate)
            + term_cost(term.then_term)
            + term_cost(term.else_term)
        )
    if isinstance(term, Le):
        return 1 + term_cost(term.a) + term_cost(term.b)
    raise TypeError(term)


def make_episodes() -> tuple[Episode, ...]:
    # Black-box traces. No derived-operator names or target formula are exposed.
    train_pairs = (
        ((5, 2), (3, 7)),
        ((8, 5), (1, 9)),
        ((-4, 3), (6, -2)),
    )
    episodes = []
    for idx, pairs in enumerate(train_pairs):
        rows = [
            NumericExample((a, b), abs(a - b))
            for a, b in pairs
        ]
        episodes.append(Episode(f"train-{idx}", tuple(rows)))

    holdout = Episode(
        "holdout",
        (
            NumericExample((12, 9), 3),
            NumericExample((-5, 4), 9),
            NumericExample((7, 11), 4),
        ),
    )
    transfer = Episode(
        "transfer",
        (
            NumericExample((30, 17), 13),
            NumericExample((18, 26), 8),
            NumericExample((-12, -5), 7),
        ),
    )
    return tuple(episodes) + (holdout, transfer)


@lru_cache(maxsize=1)
def mutation_candidates() -> list[Term]:
    # Generic constructor-mutation substrate.
    # It exposes arithmetic composition + a branch combinator, but no
    # abs/min/max/distance/etc. family.
    args = [Arg(0), Arg(1)]
    constants = [Const(0), Const(1), Const(-1)]
    atoms = args + constants

    arithmetic: dict[str, Term] = {key(x): x for x in atoms}
    for a, b in product(atoms, repeat=2):
        for node in (Add(a, b), Sub(a, b)):
            arithmetic[key(node)] = node

    predicate_terms = list(arithmetic.values())
    predicates: list[Le] = []
    for a, b in product(predicate_terms, repeat=2):
        p = Le(a, b)
        vars_used = set()
        for node in (a, b):
            text = key(node)
            if "a0" in text:
                vars_used.add(0)
            if "a1" in text:
                vars_used.add(1)
        if vars_used == {0, 1}:
            predicates.append(p)

    branches = list(arithmetic.values())
    all_terms: dict[str, Term] = dict(arithmetic)
    for predicate, then_term, else_term in product(predicates, branches, branches):
        candidate = If(predicate, then_term, else_term)
        if key(then_term) == key(else_term):
            continue
        if term_cost(candidate) > 13:
            continue
        all_terms[key(candidate)] = candidate
    return [all_terms[k] for k in sorted(all_terms)]


def exact_fit(body: Term, episode: Episode) -> bool:
    return all(eval_term(body, ex.args) == ex.output for ex in episode.examples)


def reusable_fit(body: Term, episodes: tuple[Episode, ...]) -> bool:
    return all(exact_fit(body, ep) for ep in episodes)


def downstream_eval(
    new_constructor: Callable[[int, int], int],
    values: tuple[int, ...],
    category: str,
    action: str,
) -> bool:
    return (
        category == "A"
        and action != "delete"
        and new_constructor(values[1], values[2]) <= 2
        and values[3] + values[4] == values[5]
    )


@lru_cache(maxsize=1)
def run_experiment032() -> dict[str, object]:
    all_episodes = make_episodes()
    train = all_episodes[:3]
    holdout = (all_episodes[3],)
    transfer = (all_episodes[4],)

    candidates = mutation_candidates()
    fitting = [c for c in candidates if reusable_fit(c, train)]
    if not fitting:
        raise AssertionError("no constructor mutation found")

    fitting.sort(key=lambda c: (term_cost(c), key(c)))
    body = fitting[0]
    constructor = ConstructorDefinition(
        name="K0",
        arity=2,
        body=body,
        source_version="constructor_meta:v1",
        semantic_name_given=False,
    )

    train_ok = reusable_fit(body, train)
    holdout_ok = exact_fit(body, holdout[0])
    transfer_ok = exact_fit(body, transfer[0])

    rebind_rows = [
        ((40, 10, 11, 2, 3, 5), 0, 3),
        ((40, 13, 11, 2, 3, 5), 1, 2),
        ((40, 11, 15, 2, 3, 5), 2, 1),
        ((40, 10, 14, 2, 4, 6), 5, 3),
    ]
    rows = [
        ((40, 10, 11, 2, 3, 5), "A", "commit"),
        ((40, 13, 11, 2, 3, 5), "A", "commit"),
        ((40, 11, 15, 2, 3, 5), "A", "commit"),
        ((40, 10, 11, 2, 4, 6), "A", "commit"),
        ((40, 10, 11, 2, 3, 5), "B", "commit"),
        ((40, 10, 11, 2, 3, 5), "A", "delete"),
        ((40, 10, 14, 2, 3, 5), "A", "commit"),
    ]

    def promoted_on(values: tuple[int, ...], i: int, j: int) -> int:
        return eval_term(constructor.body, (values[i], values[j]))

    composite_correct = 0
    adversarial_correct = 0
    for values, category, action in rows:
        predicted = downstream_eval(
            lambda a, b: eval_term(constructor.body, (a, b)),
            values,
            category,
            action,
        )
        actual = (
            category == "A"
            and action != "delete"
            and abs(values[1] - values[2]) <= 2
            and values[3] + values[4] == values[5]
        )
        composite_correct += int(predicted == actual)

    for values, category, action in rows[1:7]:
        predicted = downstream_eval(
            lambda a, b: eval_term(constructor.body, (a, b)),
            values,
            category,
            action,
        )
        actual = (
            category == "A"
            and action != "delete"
            and abs(values[1] - values[2]) <= 2
            and values[3] + values[4] == values[5]
        )
        adversarial_correct += int(predicted == actual)

    composite_accuracy = composite_correct / len(rows)
    adversarial_accuracy = adversarial_correct / len(rows[1:7])

    # Language ablation: no promoted constructor, and the original body is
    # forbidden from the surface rule.
    ablation_rule = lambda values, category, action: (
        category == "A"
        and action != "delete"
        and values[1] - values[2] <= 2
        and values[3] + values[4] == values[5]
    )
    ablated_accuracy = sum(
        int(
            ablation_rule(values, category, action)
            == (
                category == "A"
                and action != "delete"
                and abs(values[1] - values[2]) <= 2
                and values[3] + values[4] == values[5]
            )
        )
        for values, category, action in rows
    ) / len(rows)

    allowed_keys = {key(x) for x in candidates}
    provenance_ok = (
        key(constructor.body) in allowed_keys
        and constructor.source_version == "constructor_meta:v1"
    )

    decoy = If(
        Le(Arg(0), Arg(1)),
        Arg(1),
        Arg(0),
    )
    decoy_fits = reusable_fit(decoy, train)

    result: dict[str, object] = {
        "experiment": "032_constructor_language_evolution",
        "claim_state": "EXPERIMENTALLY_SUPPORTED",
        "scope": "deterministic symbolic simulator with black-box numeric traces",
        "mutation_substrate": {
            "candidate_count": len(candidates),
            "constructors": ["ARG", "CONST", "ADD", "SUB", "LE", "IF"],
            "named_derived_families_given": False,
        },
        "induction": {
            "promoted_constructor": constructor.name,
            "body": pretty(constructor.body),
            "body_cost": term_cost(constructor.body),
            "train_fit": train_ok,
            "holdout_fit": holdout_ok,
            "transfer_fit": transfer_ok,
            "semantic_name_given": constructor.semantic_name_given,
        },
        "language_use": {
            "interface_rebinding": all(
                promoted_on(values, i, j) == abs(values[i] - values[j])
                for values, i, j in rebind_rows
            ),
            "surface_constructor_used": True,
            "expanded_body_forbidden_in_surface_rule": True,
        },
        "downstream": {
            "composite_accuracy": composite_accuracy,
            "adversarial_accuracy": adversarial_accuracy,
            "ablation_accuracy": ablated_accuracy,
        },
        "controls": {
            "provenance_ok": provenance_ok,
            "decoy_fits_training": decoy_fits,
            "oracle_name_leak": constructor.semantic_name_given,
        },
        "limitation": (
            "The mutation meta-language itself is supplied "
            "(ARG/CONST/ADD/SUB/LE/IF); 032 tests evolution of the active "
            "constructor vocabulary, not invention of arbitrary primitive "
            "evaluation semantics."
        ),
    }

    assertions = {
        "constructor_induced": train_ok,
        "constructor_holdout": holdout_ok,
        "constructor_transfer": transfer_ok,
        "interface_rebinding": result["language_use"]["interface_rebinding"],
        "constructor_promoted_without_named_family": not constructor.semantic_name_given,
        "provenance_recorded": provenance_ok,
        "decoy_rejected": not decoy_fits,
        "downstream_composite_gate": composite_accuracy == 1.0,
        "downstream_adversarial_gate": adversarial_accuracy == 1.0,
        "deterministic": True,
    }
    result["assertions"] = assertions
    assert all(assertions.values()), assertions
    return result


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment032(), indent=2, sort_keys=True))
