# MORPHS research paths

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

043c exposed and repaired:
- Run 186: fixture encoding failure.
- Run 194: moving-ref TOCTOU between Contents and Raw surfaces.
- Run 205: stale test import after receipt API renaming.
- Run 207: tests inconsistent with the hardened transport contract.
- Run 211: tests bypassed the newly required explicit registry.
- Run 212: generated test source contained a literal escape sequence.
- Run 214: CI provenance test assumed LOCAL identifiers inside Actions.
- Run 221/222: persisted receipt revalidation reconstructed the receipt without its separately stored invocation_id.

These failures are part of the research evidence, not noise to remove.

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
- a production-grade host capability registry

These remain OPEN boundaries unless later experiments produce stronger evidence.

## 9. Next path candidates

### Path E — external runtime transfer

041 begins this path in a deterministic external-world model.

042 extends it to dependency cascades and partial external state.

043 verifies the read-only protocol model while separately recording a host-captured GitHub observation.

043b hardens the mutation protocol itself and preserves a host-captured reversible canary.

043c establishes the current runtime bridge for read-only execution:

resolve ref
→ bind capability in explicit host registry
→ enforce bound invoker
→ invoke provider
→ durable receipt
→ receipt revalidation against run/head
→ independent same-commit read
→ Git identity verification
→ explicit runtime classification

The Run 194 TOCTOU failure remains part of the design: moving refs are not accepted as sufficient cross-surface binding.

### Path E-next — independent verification and controlled uncertainty

The runtime bridge is now established for read-only GitHub execution.

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
- 043c: verified real MORPHS runtime read-only GitHub adapter with exact-commit binding, explicit host registry, bound invoker, and revalidated invocation receipt

The current decision point is provider-independent verification or controlled unknown-outcome handling before any runtime mutation attempt.
