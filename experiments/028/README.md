# Experiment 028 — Learn the Learning Mechanism

## Question

Can MORPH induce machine-level invariants from typed transitions, outcomes, interventions, controls, and transfer without being given the invariant names?

## Protocol

`observe → hypothesize → paired intervention → matched control → transfer → evidence gate`

The hidden environment enforces four invariants:
- actor authority
- budget sufficiency
- version alignment
- audit monotonicity

Two attractive but unsupported candidates are also tested:
- commit cost must be zero
- novel contexts must be blocked

## Result

- learned: p1, p2, p3, p4
- rejected: p5, p6
- 2 discriminating tests per candidate
- probe + transfer contexts
- 12 paired interventions
- reproducible under repeated execution

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope is limited to the deterministic simulator implemented in `morph_core/experiment028.py`.

This experiment does not establish autonomous real-world discovery of a complete safety constitution.
