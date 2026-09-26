# Experiment 030 — Operator Language Mutation

## Question

Can MORPH extend its own rule language when its active operator set cannot express the observed mechanism?

## Protocol

`baseline → residual failure → operator proposals → rule synthesis → holdout → transfer → adversarial → intervention → promotion`

The initial active language contains only direct typed comparisons.

A separate typed arithmetic meta-substrate allows candidate operator mutations to be proposed. MORPH must select useful derived operators rather than receiving their role or semantic meaning.

The environment contains decoy operator families and distribution shifts.

## Gates

An operator can be promoted only after:
- train support
- holdout support
- transfer support
- adversarial support
- matched intervention evidence
- lineage recording

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator.

Important limitation: the meta-substrate still supplies arithmetic constructors such as subtraction, absolute value, and addition. 030 therefore tests **language extension from a typed constructive substrate**, not unrestricted invention of arbitrary mathematical primitives.

## Research value

030 moves beyond learning rules inside a fixed language. The language itself can now change, with evidence-gated admission and explicit lineage.
