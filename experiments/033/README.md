# Experiment 033 — Meta-Language Binding Mutation

## Question

Can MORPH recognize that a resource failure is caused by the representation language, then mutate that language by adding a generic binding mechanism rather than adding a domain-specific primitive?

## Protocol

`black-box traces → over-budget fitting program → residual resource failure → repeated-subtree analysis → binding mutation → holdout → transfer → downstream reuse`

The baseline program exactly fits the traces but costs 21 units against a budget of 16.

The mutation introduces a generic `BIND/REF` mechanism and rewrites the repeated subterm once.

The promoted program costs 14 while preserving the same outputs.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator with resource-bounded black-box traces.

Limitation: the mutation method (common-subexpression abstraction) is supplied as a generic transformation. This is not unrestricted invention of arbitrary meta-semantics.
