# MORPHS research paths

## Purpose

This is the construction map for MORPHS.

It answers:
1. What are we actually assembling?
2. Through which experimental paths are we trying to assemble it?

Conversation is navigation only. Repository code, tests, captured results, and CI are the evidence source.

## 1. Construction target

The current target is a host-bounded adaptive software ecology.

The intended structure is:

stable host substrate
→ adaptive ecology
→ candidate change
→ evidence collection
→ independent or protected verification
→ promotion or DEFER
→ audit and lineage
→ revalidation

The important property is not unrestricted autonomy.

The important property is that increasingly adaptive behavior remains observable, resource-bounded, evidence-gated, and authority-separated.

## 2. Path A — learn the substrate constraints

Experiment 028 and the earlier lineage establish machine-observable invariants such as actor authority, budget sufficiency, version alignment, and audit monotonicity.

## 3. Path B — evolve the adaptive language

029-035 progressively increase what the adaptive layer can construct while remaining inside host-specified resource, interface, lineage, and evidence boundaries.

## 4. Path C — evolve verification proposals without authority

036-038 test shadow verification, verifier diversity, disagreement investigation, and DEFER-preserving diagnostics.

## 5. Shared evidence gates

Across the paths:

observe
→ identify
→ generate candidate
→ intervene
→ holdout or transfer or adversarial test
→ independent verification
→ promote or DEFER
→ record result, scope, and limitation
→ revalidate later

No stage is allowed to silently upgrade epistemic state.

## 6. Failure handling path

When a test or experiment exposes a flaw:

failure
→ classify
→ preserve failed observation
→ repair
→ rerun local affected tests
→ rerun regression
→ record changed interpretation

043 exposed an epistemic-boundary failure: host-captured live evidence had been embedded too close to deterministic runtime assertions.

043b exposed a protocol-integrity failure: state labels were treated as sufficient identity while blob identity was stored but not enforced.

043c exposed and repaired a sequence of runtime-boundary failures, including moving-ref TOCTOU, registry/invoker mismatch, CI provenance assumptions, receipt reconstruction, broader-than-needed CI token permissions, and a recomputed-receipt replay regression fixture.

These failures are part of the research evidence, not noise to remove.

## 7. Authority graph

HOST
→ controls execution boundaries
→ controls verifier integrity
→ controls audit integrity
→ authorizes external side effects

ADAPTIVE ECOLOGY
→ proposes capabilities
→ proposes rules and operators
→ proposes policies
→ proposes shadow verifiers
→ proposes investigation targets

PROTECTED VERIFICATION
→ evaluates proposals against evidence

AUDIT
→ records what happened, why a change was accepted or deferred, and under which scope

No arrow from adaptive proposal state points directly to host authority.

## 8. Current non-claims

The present lineage does not establish:
- unrestricted self-modification
- unrestricted self-rewriting of verifier semantics
- semantic independence of arbitrary verifier implementations
- unrestricted automated root-cause identification
- provider-independent verification
- cryptographic receipt authenticity
- MORPHS runtime mutation of external systems
- real ambiguous mutation outcomes
- irreversible mutation safety
- rollback of arbitrary external side effects
- distributed transaction semantics
- resilience against adversarial corruption of verifier inputs or investigation traces
- provider substitution under contract equivalence
- production-grade host capability isolation
- strong post-response freshness semantics

These remain OPEN boundaries unless later experiments produce stronger evidence.

## 9. Next path candidates

### Path E — external runtime transfer

041 begins this path in a deterministic external-world model.

042 extends it to dependency cascades and partial external state.

043 verifies the read-only protocol model while separately recording a host-captured GitHub observation.

043b hardens the mutation protocol itself and preserves a host-captured reversible canary.

043c establishes the current runtime bridge for read-only execution:

resolve ref
→ bind capability through injected host registry
→ require bound invoker
→ invoke provider
→ durable receipt
→ revalidate receipt against trusted CI run/head
→ independent same-commit read
→ Git identity verification
→ explicit runtime classification

The Run 194 TOCTOU failure remains part of the design: moving refs are not accepted as sufficient cross-surface binding.

The latest replay regression also established that receipt self-consistency is not enough; trusted CI provenance is required to detect recomputed receipt replay.

### Path E-next — independent verification and controlled uncertainty

The runtime bridge is now established for one read-only GitHub capability.

The next research gate is deliberately narrower:

provider-independent verification
or
controlled unknown-outcome handling at the provider-adapter boundary

Runtime mutation stays blocked until that gate yields stronger evidence.

### Path F — adversarial verification pressure

Let the adaptive layer attempt to influence:
- verifier inputs
- audit traces
- disagreement probes
- evidence selection

while keeping verification authority protected.

These are branches of one construction, not separate projects.

## 10. Current research state

- 039: verified protocol grounding
- 040: verified reversible adaptation
- 041: verified deterministic external-world equilibrium
- 042: verified dependency cascades and partial external failure
- 043: corrected protocol boundary; host-captured live read evidence; runtime integration OPEN
- 043b: corrected mutation identity/authority boundary; host-captured reversible canary; runtime mutation OPEN
- 043c: verified real MORPHS runtime read-only GitHub adapter with exact-commit binding, injected host registry, bound invoker, trusted receipt provenance, and replay-resistant revalidation

The current decision point is provider-independent verification or controlled unknown-outcome handling before any runtime mutation attempt.
