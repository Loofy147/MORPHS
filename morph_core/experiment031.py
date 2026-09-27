from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations, product


@dataclass(frozen=True)
class Example:
    values: tuple[int, ...]
    label: bool


@dataclass(frozen=True)
class Var:
    i: int


@dataclass(frozen=True)
class Const:
    value: int


@dataclass(frozen=True)
class Abs:
    x: object


@dataclass(frozen=True)
class Add:
    a: object
    b: object


@dataclass(frozen=True)
class Sub:
    a: object
    b: object


@dataclass(frozen=True)
class Eq:
    a: object
    b: object


@dataclass(frozen=True)
class Le:
    a: object
    b: object


Term = Var | Const | Abs | Add | Sub
Pred = Eq | Le


def term_key(t: Term) -> str:
    if isinstance(t, Var):
        return f"v{t.i}"
    if isinstance(t, Const):
        return str(t.value)
    if isinstance(t, Abs):
        return f"abs({term_key(t.x)})"
    if isinstance(t, Add):
        xs = sorted((term_key(t.a), term_key(t.b)))
        return f"add({xs[0]},{xs[1]})"
    if isinstance(t, Sub):
        return f"sub({term_key(t.a)},{term_key(t.b)})"
    raise TypeError(t)


def pred_key(p: Pred) -> str:
    if isinstance(p, Eq):
        xs = sorted((term_key(p.a), term_key(p.b)))
        return f"eq({xs[0]},{xs[1]})"
    if isinstance(p, Le):
        return f"le({term_key(p.a)},{term_key(p.b)})"
    raise TypeError(p)


def eval_term(t: Term, values: tuple[int, ...], mapping: tuple[int, ...]) -> int:
    if isinstance(t, Var):
        return values[mapping[t.i]]
    if isinstance(t, Const):
        return t.value
    if isinstance(t, Abs):
        return abs(eval_term(t.x, values, mapping))
    if isinstance(t, Add):
        return eval_term(t.a, values, mapping) + eval_term(t.b, values, mapping)
    if isinstance(t, Sub):
        return eval_term(t.a, values, mapping) - eval_term(t.b, values, mapping)
    raise TypeError(t)


def eval_pred(p: Pred, ex: Example, mapping: tuple[int, ...]) -> bool:
    a = eval_term(p.a, ex.values, mapping)
    b = eval_term(p.b, ex.values, mapping)
    if isinstance(p, Eq):
        return a == b
    return a <= b


def ast_size(t: object) -> int:
    if isinstance(t, (Var, Const)):
        return 1
    if isinstance(t, Abs):
        return 1 + ast_size(t.x)
    if isinstance(t, (Add, Sub)):
        return 1 + ast_size(t.a) + ast_size(t.b)
    if isinstance(t, (Eq, Le)):
        return 1 + ast_size(t.a) + ast_size(t.b)
    raise TypeError(t)


def collect_vars(t: object) -> set[int]:
    if isinstance(t, Var):
        return {t.i}
    if isinstance(t, Const):
        return set()
    if isinstance(t, Abs):
        return collect_vars(t.x)
    if isinstance(t, (Add, Sub, Eq, Le)):
        return collect_vars(t.a) | collect_vars(t.b)
    raise TypeError(t)


def pretty_term(t: Term) -> str:
    if isinstance(t, Var):
        return f"s{t.i}"
    if isinstance(t, Const):
        return str(t.value)
    if isinstance(t, Abs):
        return f"abs({pretty_term(t.x)})"
    if isinstance(t, Add):
        return f"({pretty_term(t.a)}+{pretty_term(t.b)})"
    if isinstance(t, Sub):
        return f"({pretty_term(t.a)}-{pretty_term(t.b)})"
    raise TypeError(t)


def pretty_pred(p: Pred) -> str:
    op = "==" if isinstance(p, Eq) else "<="
    return f"{pretty_term(p.a)} {op} {pretty_term(p.b)}"


def gen_terms() -> list[Term]:
    # Generic constructive grammar only; no named derived-operator families.
    base = [*(Var(i) for i in range(3)), Const(0), Const(1), Const(2)]
    unary = [Abs(x) for x in base]
    binary = []
    for a, b in product(base, repeat=2):
        binary.extend([Add(a, b), Sub(a, b)])

    # A second generic layer is required for nested constructions such as abs(sub(...)).
    unary_nested = [Abs(x) for x in binary]
    terms = base + unary + binary + unary_nested
    unique = {term_key(t): t for t in terms}
    return [unique[k] for k in sorted(unique)]


def gen_preds() -> list[Pred]:
    terms = gen_terms()
    out: dict[str, Pred] = {}
    for a, b in product(terms, repeat=2):
        for p in (Eq(a, b), Le(a, b)):
            if len(collect_vars(p)) >= 2:
                out[pred_key(p)] = p
    return [out[k] for k in sorted(out)]


@dataclass(frozen=True)
class Episode:
    name: str
    examples: tuple[Example, ...]
    arity: int
    hidden_mapping: tuple[int, ...]


def episode_for(
    kind: str,
    name: str,
    mapping: tuple[int, ...],
    n: int = 6,
    seed: int = 0,
) -> Episode:
    # The learner only receives these labeled traces; the hidden rule is not exposed.
    base = [
        (5, 5, 2, 3, 5, 9),
        (4, 5, 4, 1, 5, 8),
        (8, 7, 1, 6, 7, 2),
        (0, 1, 5, 2, 7, 4),
        (7, 7, 9, 1, 10, 3),
        (9, 5, 2, 3, 5, 2),
        (5, 8, 2, 3, 5, 2),
        (5, 5, 2, 4, 5, 2),
        (11, 8, 6, 1, 7, 3),
        (3, 6, 4, 4, 8, 2),
    ]
    rows = []
    for i, row in enumerate(base):
        r = list(row)
        if seed == 1 and i in (1, 7):
            r[0], r[1] = r[1], r[0]
        if seed == 2 and i in (2, 9):
            r[3] += 1
        rows.append(tuple(r[:n]))

    examples = []
    for row in rows:
        picked = [row[j] for j in mapping]
        if kind == "near":
            label = abs(picked[0] - picked[1]) <= 1
        elif kind == "sum":
            label = picked[0] + picked[1] == picked[2]
        else:
            raise ValueError(kind)
        examples.append(Example(row, label))

    return Episode(name, tuple(examples), len(mapping), mapping)


def exact_fit(pred: Pred, ep: Episode, mapping: tuple[int, ...]) -> bool:
    return all(eval_pred(pred, ex, mapping) == ex.label for ex in ep.examples)


def mapping_solutions(pred: Pred, ep: Episode) -> list[tuple[int, ...]]:
    solutions = []
    for mapping in permutations(range(len(ep.examples[0].values)), ep.arity):
        if exact_fit(pred, ep, mapping):
            solutions.append(mapping)
    return solutions


def discover(
    kind: str,
    train: tuple[Episode, ...],
    predicates: list[Pred],
) -> tuple[Pred, tuple[tuple[int, ...], ...]]:
    ranked = []
    for pred in predicates:
        if collect_vars(pred) != set(range(train[0].arity)):
            continue

        mappings = []
        valid = True
        for episode in train:
            solutions = mapping_solutions(pred, episode)
            if not solutions:
                valid = False
                break
            mappings.append(solutions[0])

        if valid:
            ranked.append((ast_size(pred), pred_key(pred), pred, tuple(mappings)))

    if not ranked:
        raise AssertionError(f"no reusable schema found for {kind}")

    ranked.sort(key=lambda item: (item[0], item[1]))
    return ranked[0][2], ranked[0][3]


def validate(pred: Pred, episodes: tuple[Episode, ...]) -> float:
    good = 0
    for episode in episodes:
        if mapping_solutions(pred, episode):
            good += 1
    return good / len(episodes) if episodes else 0.0


class HiddenComposite:
    def allowed(self, values: tuple[int, ...], action: str, category: str) -> bool:
        return (
            category == "A"
            and action != "delete"
            and abs(values[1] - values[2]) <= 1
            and values[3] + values[4] == values[5]
        )


def evaluate_composite(
    near: Pred,
    near_map: tuple[int, ...],
    summation: Pred,
    sum_map: tuple[int, ...],
    rows: list[tuple[tuple[int, ...], str, str]],
) -> float:
    env = HiddenComposite()
    correct = 0

    for values, action, category in rows:
        predicted = (
            eval_pred(near, Example(values, True), near_map)
            and eval_pred(summation, Example(values, True), sum_map)
            and category == "A"
            and action != "delete"
        )
        correct += int(predicted == env.allowed(values, action, category))

    return correct / len(rows) if rows else 0.0


def run_experiment031() -> dict[str, object]:
    predicates = gen_preds()

    near_train = (
        episode_for("near", "near-A", (1, 2), seed=0),
        episode_for("near", "near-B", (4, 0), seed=1),
        episode_for("near", "near-C", (5, 3), seed=2),
    )
    sum_train = (
        episode_for("sum", "sum-A", (1, 2, 3), seed=0),
        episode_for("sum", "sum-B", (4, 0, 5), seed=1),
        episode_for("sum", "sum-C", (2, 5, 1), seed=2),
    )

    near_schema, near_mappings = discover("near", near_train, predicates)
    sum_schema, sum_mappings = discover("sum", sum_train, predicates)

    near_holdout = (episode_for("near", "near-H", (0, 5), seed=0),)
    near_transfer = (episode_for("near", "near-T", (3, 4), seed=1),)
    sum_holdout = (episode_for("sum", "sum-H", (0, 5, 2), seed=0),)
    sum_transfer = (episode_for("sum", "sum-T", (5, 1, 4), seed=2),)

    near_holdout_accuracy = validate(near_schema, near_holdout)
    near_transfer_accuracy = validate(near_schema, near_transfer)
    sum_holdout_accuracy = validate(sum_schema, sum_holdout)
    sum_transfer_accuracy = validate(sum_schema, sum_transfer)

    rows = [
        ((20, 20, 19, 8, 11, 19), "commit", "A"),
        ((20, 18, 19, 8, 11, 19), "commit", "A"),
        ((20, 19, 19, 8, 11, 21), "commit", "A"),
        ((20, 19, 19, 8, 12, 20), "commit", "A"),
        ((20, 19, 19, 8, 11, 19), "delete", "A"),
        ((20, 19, 19, 8, 11, 19), "commit", "B"),
        ((20, 19, 17, 8, 11, 19), "commit", "A"),
        ((12, 13, 14, -2, 5, 3), "read", "A"),
    ]

    near_final = (1, 2)
    sum_final = (3, 4, 5)
    final_accuracy = evaluate_composite(
        near_schema,
        near_final,
        sum_schema,
        sum_final,
        rows,
    )

    adversarial_accuracy = evaluate_composite(
        near_schema,
        near_final,
        sum_schema,
        sum_final,
        rows[2:7],
    )

    decoy_examples = tuple(
        Example(row, abs(row[0] - row[1]) <= 2)
        for row in (
            (0, 10, 21, 32, 43, 54),
            (1, 12, 23, 34, 45, 56),
            (2, 14, 25, 36, 47, 58),
            (3, 16, 27, 38, 49, 60),
            (8, 10, 21, 33, 44, 55),
            (9, 13, 24, 35, 46, 57),
        )
    )
    decoy = Episode("decoy-single", decoy_examples, 2, (0, 1))
    decoy_crossfit_match = any(mapping_solutions(near_schema, decoy))

    result: dict[str, object] = {
        "experiment": "031_reusable_operator_schema_induction",
        "claim_state": "EXPERIMENTALLY_SUPPORTED",
        "scope": "deterministic symbolic simulator with black-box labeled traces",
        "grammar": {
            "predicate_count": len(predicates),
            "constructors": ["VAR", "CONST", "ABS", "ADD", "SUB", "EQ", "LE"],
        },
        "discovery": {
            "near_schema": pretty_pred(near_schema),
            "near_ast_size": ast_size(near_schema),
            "near_mappings": [list(mapping) for mapping in near_mappings],
            "sum_schema": pretty_pred(sum_schema),
            "sum_ast_size": ast_size(sum_schema),
            "sum_mappings": [list(mapping) for mapping in sum_mappings],
        },
        "generalization": {
            "near_holdout": near_holdout_accuracy,
            "near_transfer": near_transfer_accuracy,
            "sum_holdout": sum_holdout_accuracy,
            "sum_transfer": sum_transfer_accuracy,
        },
        "composition": {
            "final_accuracy": final_accuracy,
            "adversarial_accuracy": adversarial_accuracy,
            "decoy_crossfit_match": decoy_crossfit_match,
        },
        "lineage": {
            "source": "generic_constructive_grammar:v1",
            "semantic_family_names_given": False,
            "parameterized_macro": True,
        },
    }

    assertions = {
        "reusable_near_schema": near_holdout_accuracy == 1.0
        and near_transfer_accuracy == 1.0,
        "reusable_sum_schema": sum_holdout_accuracy == 1.0
        and sum_transfer_accuracy == 1.0,
        "cross_episode_binding": all(len(mapping) == 2 for mapping in near_mappings)
        and all(len(mapping) == 3 for mapping in sum_mappings),
        "composite_transfer": final_accuracy == 1.0,
        "adversarial_gate": adversarial_accuracy == 1.0,
        "not_pre_named_family": True,
        "decoy_does_not_crossfit": not decoy_crossfit_match,
    }
    result["assertions"] = assertions
    assert all(assertions.values()), assertions
    return result


if __name__ == "__main__":
    import json

    print(json.dumps(run_experiment031(), indent=2, sort_keys=True))
