# Experiment 029 — Induced Rule Language

## Question

Can MORPH construct and search a machine-level rule language from typed observations, without being given human semantic rule names?

## Design

The environment exposes only typed, observable state fields:
- one categorical field
- one categorical action
- numeric fields
- opaque context labels

The learner receives an operator grammar (equality, inequality, numeric comparison, conjunction), not domain explanations.

Training contains deliberate decoys:
- context correlates with outcomes
- familiar labels are not reliable
- transfer reverses the decoy correlations

MORPH:
1. generates atomic predicates from the machine-level type system
2. ranks discriminative atoms
3. composes them into candidate rules
4. tests candidates on holdout and transfer contexts
5. runs matched intervention pairs
6. keeps only candidates supported by all gates

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope is limited to the deterministic symbolic simulator.

This does not establish open-ended invention of new formal languages, nor real-world autonomous scientific discovery.

## Research value

029 removes the human semantic names used in 028 while retaining only a typed operator substrate. The next frontier is to let MORPH invent or modify the operator set itself rather than receiving it as part of the environment contract.
