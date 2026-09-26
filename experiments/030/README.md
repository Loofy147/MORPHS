# Experiment 030 — Operator Language Mutation

## Question

Can MORPH extend its own rule language when its active operator set cannot express the observed mechanism?

## Protocol

`baseline → residual failure → operator proposals → rule synthesis → holdout → transfer → adversarial → intervention → promotion`

The initial active language contains only direct typed comparisons.

A separate typed arithmetic meta-substrate allows candidate operator mutations to be proposed. MORPH must select useful derived operators rather than receiving their role or semantic meaning.

The environment contains decoy operator families and distribution shifts.

## Gates

The **composite rule** must pass:
- train
- holdout
- transfer
- adversarial

Each selected new operator must additionally show:
- positive-state consistency across contexts
- discriminative contribution
- matched intervention evidence
- lineage recording
- non-decoy family status

## CI repair recorded

The first implementation incorrectly scored each operator against the **full environment outcome**. CI rejected that design because a condition can be a necessary component of a composite rule without explaining every negative state by itself.

The repaired admission separates:
- **operator evidence**: consistency + discrimination + intervention
- **composite evidence**: complete rule correctness on train/holdout/transfer/adversarial

This distinction is now part of the experiment record.

## Verified result

GitHub Actions run `36257127559` completed successfully with compile, pytest, Experiment 028, Experiment 029, and Experiment 030 all green.

Promoted operators:
- `abs(x1-x2) <= 1`
- `x3+x4 == x5`

Composite rule:

`abs(x1-x2) <= 1 AND action != delete AND x0 == A AND x3+x4 == x5`

Composite accuracy:
- train: 1.0
- holdout: 1.0
- transfer: 1.0
- adversarial: 1.0

Proposal count: 135.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator.

Important limitation: the meta-substrate still supplies arithmetic constructors such as subtraction, absolute value, and addition. 030 therefore tests **language extension from a typed constructive substrate**, not unrestricted invention of arbitrary mathematical primitives.

## Research value

030 moves beyond learning rules inside a fixed language. The language itself can now change, with evidence-gated admission and explicit lineage.

See `experiments/030/result.json` for the recorded result and repair history.
