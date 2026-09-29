# Experiment 043b — Authorized Reversible Mutation

## Research question

Can the mutation protocol require exact pre-state identity, bound authorization, idempotency, independent postcondition, unknown-outcome containment, and rollback revalidation?

## Critical epistemic boundary

043b contains two different evidence surfaces:

1. A deterministic MORPHS protocol model, executed by CI.
2. A host-captured live GitHub canary mutation/rollback, executed through GitHub tooling outside the MORPHS experiment module.

The second is real external evidence, but it is not evidence that MORPHS itself invoked the provider.

Therefore:

- protocol semantics: EXPERIMENTALLY_SUPPORTED
- MORPHS runtime integration with GitHub mutation: OPEN
- provider-independent verification: OPEN

This distinction is part of the experiment, not a footnote.

## Safety boundary

The live canary used exactly one text file on:

experiment-043b-canary:experiments/043b/live_canary.txt

The branch was isolated from main.

No application code, credentials, production-like resource, or irreversible side effect was used.

## Corrected protocol

PRE_READ -> AUTHORITY_CHECK -> IDEMPOTENCY_CHECK -> MUTATE -> INDEPENDENT_POST_READ -> VERIFY -> ROLLBACK_PREFLIGHT -> ROLLBACK -> REVALIDATE

The protocol now requires both semantic state and content identity.

A matching state label with a different blob identity is not considered the same state.

Authorization is also bound to:

- capability identity
- resource scope
- declared side effects

## Live host-captured evidence

The host-side canary mutation produced:

- baseline blob 1831c4b6...
- mutation commit a8506777...
- mutated blob 6bc77249...
- rollback commit 6a47d4db...
- final blob restored to 1831c4b6...

Two GitHub read surfaces agreed after mutation and after rollback.

This establishes a real provider observation and compensation sequence.

It does not establish that the MORPHS runtime executed the mutation.

## Adversarial cases now protected

- desired state with wrong blob identity -> DEFER
- expected baseline state with wrong blob identity -> DEFER
- postcondition with wrong blob identity -> DEFER
- rollback after same-state content drift -> DEFER
- rollback postcondition with wrong target blob -> DEFER
- authorization bound to another capability or scope -> reject
- unknown outcome with only a matching state label -> DEFER

## Preserved audit finding

The first 043b implementation treated state as sufficient identity and stored blob_sha without using it as a safety predicate. Direct adversarial reproduction showed four false-positive paths:

- idempotency could accept a wrong blob
- postcondition could accept a wrong blob
- rollback preflight could accept a wrong blob
- rollback verification could accept a wrong blob

The implementation was hardened so identity now includes state + blob.

A second epistemic finding was that the live GitHub mutation was performed by host tooling, while the CI experiment was a deterministic simulator. The runtime claim has therefore been explicitly downgraded to OPEN.

## What remains OPEN

- MORPHS runtime -> GitHub adapter execution
- provider-independent mutation verification
- real ambiguous network outcome
- irreversible side-effect safety
- distributed transaction semantics
- adversarial provider state reporting
- long-lived drift after rollback
- provider substitution under contract equivalence

## Next boundary

043c should establish one missing layer only:

provider-adapter execution with a durable receipt that can be independently verified.

Only after that should we consider a real ambiguity-injection experiment.
