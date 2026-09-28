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

This layer is not the object of unrestricted learner modification.

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
- disagreement-investigation targets

An adaptive artifact is evidence-bearing state. It does not become authority merely because it is learned.

## Authority boundary

A proposal is not an execution authority.

A learned rule is not automatically a permission.

An observation is not automatically a capability.

An experiment result is evidence with scope, not a universal truth.

A shadow verifier is not the verifier authority.

An investigation target is not a truth verdict.

The host kernel owns promotion, verifier integrity, audit integrity, and external side-effect authorization.

## Research construction path

The native experiments are building one bounded organism from two coupled paths.

### Adaptive-language path

028 constitution induction
→ 029 fixed rule-language induction
→ 030 operator-language evolution
→ 031 reusable parameterized schemas
→ 032 constructor-vocabulary evolution
→ 033 meta-language mutation under resource pressure
→ 034 budget-aware reuse/evolve/defer
→ 035 memory drift and constructor revalidation

This path asks how the adaptive ecology can change its representational and procedural machinery while remaining inside explicit resource, lineage, memory, and evidence constraints.

### Verification-authority path

036 shadow verifier evolution
→ 037 independent verifier diversity
→ 038 disagreement investigation

This path asks how learned verification machinery can be proposed and tested without allowing the learner to acquire verifier authority.

The two paths meet at promotion:

proposal → independent evidence → protected verification → promotion or DEFER → audit record

## Native protocol baseline

MORPHS now has a host-specified native protocol baseline in docs/MORPHS_PROTOCOLS.md. The protocol separates host constraints from adaptive artifacts and keeps protocol status separate from epistemic research status.

039 makes one part of that separation executable: known protocol facts are used as constraints, unknown mechanisms become experiment questions, contradictions are preserved, and known failures become regression targets.

## Current boundary

036 made shadow verifier evolution executable while keeping the kernel protected.

037 added verifier diversity and established DEFER when independent verifier implementations disagree.

038 adds a bounded diagnostic layer: the system may investigate the source of disagreement, but the investigation itself cannot promote a truth verdict.

039 adds protocol grounding: the system may receive high-level host facts without treating those facts as discoveries, while keeping unknown mechanisms open to evidence-gated experimentation.

040 adds reversible adaptation: promoted versions can be rolled back only with host authority and current revalidation; history is preserved and stale rollback is blocked.

041 adds the external-world boundary: reconciliation is based on fresh observation and dependency satisfaction, not internal memory. Unknown external outcomes require observation before replay.

042 adds dependency-cascade semantics and a distinct PARTIAL state: an upstream dependency failure can block an entire downstream branch, while a mutation failure after earlier mutations leaves observable partial state that must be reconciled explicitly.

## Assembly intent

The project is not currently trying to prove unrestricted self-modification.

It is assembling a host-bounded adaptive system with:
- explicit authority boundaries
- reproducible experiments
- evidence-gated promotion
- independent verification
- preserved failed observations
- memory revalidation
- explicit residual uncertainty
- a growing but auditable adaptive language

This distinction is central to every subsequent experiment.

## Evidence discipline

When a flaw is exposed:
1. classify the flaw
2. preserve the failed observation
3. change the experiment or implementation
4. rerun the affected tests
5. rerun the regression suite
6. record the changed interpretation

The experiment lineage must describe what the system can do, what remains supplied by the host, and what remains OPEN.
