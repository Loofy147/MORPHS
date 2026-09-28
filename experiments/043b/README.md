# Experiment 043b — Authorized Reversible Mutation

## Research question

Can MORPHS perform a narrowly authorized external mutation, verify its postcondition independently, contain unknown outcomes, and roll back only when the current state still matches the expected mutated state?

## Safety boundary

043b is intentionally smaller than "external orchestration".

It mutates exactly one text file on a dedicated GitHub branch:

experiment-043b-canary:experiments/043b/live_canary.txt

The branch is isolated from main.

No application code, test code, workflow definition, credentials, production-like resource, or irreversible side effect is used.

## Protocol

PRE_READ -> AUTHORITY_CHECK -> IDEMPOTENCY_CHECK -> MUTATE -> INDEPENDENT_POST_READ -> VERIFY -> ROLLBACK_PREFLIGHT -> ROLLBACK -> REVALIDATE

The rollback preflight is deliberately protected:

current state must still equal the expected mutated state before rollback is authorized.

This prevents rollback from overwriting a new external change that happened after the mutation.

## Live execution

### Baseline

Created the canary with:

state=baseline
version=1

Baseline blob SHA:

1831c4b6a79350f2b5cb75729be015b0b9c46228

### Mutation

Authorized write changed the same file to:

state=mutated
version=2

Mutation commit:

a8506777be2ef5f7c7ba302b8cf982fd5bec8d36

Mutated blob SHA:

6bc77249dbb9001daee2d677b9a6b4fa476220f7

Independent GitHub raw read matched the repository-contents read after mutation.

### Rollback

Rollback restored the original baseline content.

Rollback commit:

6a47d4db094839bfb2193a81449f7d69690df216

Final blob SHA:

1831c4b6a79350f2b5cb75729be015b0b9c46228

Independent GitHub raw read matched the contents read after rollback.

Therefore the live run ended at the exact original blob identity.

## Deterministic safety cases

The experiment also protects these cases:

- baseline differs from expected pre-state -> DEFER
- desired state already present -> NOOP_ALREADY_APPLIED
- provider outcome unknown -> read current state before any retry
- unknown state is unexpected/partial -> DEFER, no blind retry
- provider reports success but post-read disagrees -> DEFER
- rollback target has drifted -> DEFER, do not overwrite it
- rollback post-read must match the original target

## Epistemic status

EXPERIMENTALLY_SUPPORTED

Scope: one real, reversible GitHub file mutation on an isolated branch plus deterministic protocol regression.

## What this does NOT establish

- safe mutation of arbitrary external systems
- irreversible side-effect safety
- distributed transaction semantics
- real ambiguous network outcomes
- provider-independent mutation verification
- safe provider substitution
- adversarial provider state reporting
- long-lived external drift handling after rollback

These remain OPEN.

## Preserved engineering rules

Unknown outcome -> observe before retry.

Rollback -> new state transition + revalidation, never deletion of history.

Rollback must not clobber post-mutation drift.

## Next boundary

043c should first strengthen verification independence or deliberately inject an ambiguous outcome at the provider-adapter boundary before expanding the external side-effect surface.
