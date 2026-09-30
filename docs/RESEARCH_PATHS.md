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

043c exposed two different classes:
- Run 186: TEST_FIXTURE_FAILURE from an incorrectly encoded fixture.
- Run 194: EXTERNAL_CONSISTENCY_FAILURE / TOCTOU caused by verifying two provider surfaces against a moving branch ref.

The Run 194 result was DEFER, not retry.

The repair resolved the requested branch ref to an exact commit and required both provider surfaces to use that immutable commit.

Run 196 revalidated the repaired runtime adapter.

These failures are part of the research evidence, not noise to remove.

## 8. Current non-claims

The present lineage does not establish:
- unrestricted self-modification
- unrestricted self-rewriting of verifier semantics
- semantic independence of arbitrary verifier implementations
- unrestricted automated root-cause identification
- provider-independent verification
- MORPHS runtime mutation of external systems
- real ambiguous mutation outcomes
- irreversible mutation safety
- rollback of arbitrary external side effects
- distributed transaction semantics
- resilience against adversarial corruption of verifier inputs or investigation traces
- provider substitution under contract equivalence
- full host capability-registry integration for 043c

These remain OPEN boundaries unless later experiments produce stronger evidence.

## 9. Next path candidates

### Path E — external runtime transfer

041 begins this path in a deterministic external-world model.

042 extends it to dependency cascades and partial external state.

043 verifies the read-only protocol model while separately recording a host-captured GitHub observation.

043b hardens the mutation protocol itself and preserves a host-captured reversible canary.

043c establishes the runtime bridge for read-only execution:

resolve ref
→ invoke provider
→ durable receipt
→ independent same-commit read
→ Git identity verification
→ explicit runtime classification

The Run 194 TOCTOU failure is now part of the design: moving refs are not accepted as sufficient cross-surface binding.

### Path E-next — capability-registry integration and durable runtime evidence

The next research step is:

host capability registry
→ adapter binding
→ invocation
→ durable receipt artifact
→ independent verification
→ explicit evidence classification

Only after this bridge is established should runtime mutation be considered again.

## 10. Current research state

- 039: verified protocol grounding
- 040: verified reversible adaptation
- 041: verified deterministic external-world equilibrium
- 042: verified dependency cascades and partial external failure
- 043: corrected protocol boundary; host-captured live read evidence; runtime integration OPEN
- 043b: corrected mutation identity/authority boundary; host-captured reversible canary; runtime mutation OPEN
- 043c: verified real MORPHS runtime read-only GitHub adapter with exact-commit binding and hash-bound receipt

The current decision point is capability-registry integration before any runtime mutation.
