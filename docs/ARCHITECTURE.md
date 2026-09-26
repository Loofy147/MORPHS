# MORPHS architecture baseline

## Stable substrate

The stable substrate is the machine-enforced layer:
- host-controlled execution
- resource budgets
- version and lineage checks
- append-oriented audit traces
- explicit epistemic states
- evidence-gated promotion

## Adaptive ecology

The adaptive layer may evolve:
- capabilities
- workflows
- memory policies
- hypotheses
- experiment policies
- conditional rules

## Authority boundary

A proposal is not an execution authority.

A learned rule is not automatically a permission.

An observation is not automatically a capability.

An experiment result is evidence with scope, not a universal truth.

## Current research direction

After 028, MORPH is being moved from a sequence of isolated simulators toward a persistent research environment in which:
- experiments are first-class objects
- evidence has lineage
- memory has different classes
- contradictions remain queryable
- the learner can construct candidate rule languages
- external tools can be attached through explicit adapters

The next experiment should be implemented natively in this repository rather than as an external zip snapshot.
