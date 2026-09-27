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
- reusable operator schemas

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
- reusable operator schemas can be induced and rebound
- external tools can be attached through explicit adapters

031 establishes a stronger boundary than 030: the learner is not handed named derived-operator families, but it still works inside a supplied constructive AST vocabulary.

The next experiment should attack that remaining boundary: constructor-language evolution itself, with explicit controls against hidden-oracle leakage and loss of verifier authority.
