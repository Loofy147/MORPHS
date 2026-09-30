# Experiment 043c — Real Runtime Adapter and Invocation Receipt

## Research question

Can MORPHS itself invoke a real external provider through a bounded runtime adapter, retain an invocation receipt, independently read the same resource through a second provider surface, and verify content plus provider identity before classifying the observation?

## Why this follows the audit

043 and 043b exposed an important distinction:

host-side GitHub tooling performing an action is not the same evidence as the MORPHS runtime performing that action.

043c tests that missing bridge.

It deliberately remains read-only.

## Runtime boundary

Provider: GitHub

Operation: read `README.md` from `Loofy147/MORPHS@main`

The primary surface is the GitHub Contents API.

The independent surface is GitHub Raw Content.

The Python experiment invokes both surfaces itself from GitHub Actions.

## Verified live execution

GitHub Actions run **189** passed on commit:

`c7fa5ac93a601eacf9711bec1c0874b63358da71`

The runtime:

- performed a real HTTP GET against the GitHub Contents API,
- received HTTP 200,
- recorded a provider request id and ETag,
- independently read the same file through the raw surface,
- matched the two byte streams,
- recomputed the Git blob identity,
- matched the provider-reported blob SHA,
- produced a hash-bound invocation receipt.

The durable receipt is stored in `experiments/043c/result.json`.

## Verification rule

The live observation is VERIFIED only when:

1. the runtime invocation returns successfully,
2. the API response is a file,
3. the API content decodes successfully,
4. raw content matches byte-for-byte,
5. Git blob identity computed from the observed content matches the provider blob SHA,
6. the invocation receipt is complete and internally hash-bound,
7. repository/path/ref binding remains exact,
8. receipt tampering tests reject modified identity/hash fields.

Otherwise the experiment fails instead of upgrading the evidence state.

## Preserved failure

Run **186** failed before reaching the live provider because a unit fixture encoded the string incorrectly.

The fixture decoded to `MORPSS-043C`, not `MORPHS-043C`.

This was classified as `TEST_FIXTURE_FAILURE`, repaired, and revalidated by Runs 187-189.

## Epistemic limits

This establishes:

`MORPHS runtime -> real GitHub read-only provider`

It still does not establish:

- provider-independent verification
- mutation through the MORPHS runtime
- ambiguous network outcome handling
- irreversible effects
- rollback
- distributed transaction semantics
- host capability-registry integration

Those remain OPEN.
