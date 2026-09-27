# MORPHS architecture baseline

## Stable substrate

The stable substrate is the machine-enforced layer:
- host-controlled execution
- resource budgets
- version and lineage checks
- append-oriented audit traces
- explicit epistemic states
- evidence-gated promotion
- protected verifier authority

## Adaptive ecology

The adaptive layer may evolve:
- capabilities
- workflows
- memory policies
- hypotheses
- experiment policies
- conditional rules
- reusable operator schemas
- shadow verifier proposals

## Authority boundary

A proposal is not an execution authority.

A learned rule is not automatically a permission.

An observation is not automatically a capability.

An experiment result is evidence with scope, not a universal truth.

A shadow verifier is not the verifier authority.

The host kernel owns promotion and verifier integrity.

## Current research direction

MORPH now has experimental evidence for evolving operators, language structure, budget-aware mutation, memory revalidation, and shadow verifier proposals.

036 makes the authority boundary executable:
- candidate verifier logic can be proposed and tested
- protected evidence gates remain outside candidate control
- promotion is decided by an immutable host kernel
- self-granted verifier authority is denied

The next experiment should introduce independent verifier diversity, so success cannot depend on matching one implementation of the kernel.
