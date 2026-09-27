# Experiment 034 — Budget-Aware Language Evolution

## Question

Can MORPH decide when language evolution is worth its resource cost, rather than always mutating when a mutation exists?

## Policy

The allocator uses hard feasibility gates for budget and mutation risk, then compares reuse versus evolution only when both are admissible.

Scenarios intentionally cover:
- stable reuse
- blocked frontier
- expensive mutation
- uncertain mutation

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic decision simulator.

The values and costs are scenario inputs; this experiment supports policy behavior under explicit gates, not a universal utility function.
