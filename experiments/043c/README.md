# Experiment 043c — Real Runtime Adapter and Invocation Receipt

## Research question

Can MORPHS itself invoke a real external provider through a bounded runtime adapter, retain an invocation receipt, independently read the same resource through a second provider surface, and verify content plus provider identity before classifying the observation?

## Critical runtime boundary

043c is a **read-only** experiment.

The MORPHS Python runtime itself performs the HTTP calls. This is materially different from the host-captured GitHub action in 043b.

## Ref binding rule

A moving branch ref is not sufficient for cross-surface verification.

The adapter now:

1. resolves the requested ref (for this experiment, \`main\`) to an exact commit SHA,
2. reads the GitHub Contents API at that exact commit,
3. reads the GitHub Raw surface at the same exact commit,
4. binds both observations and the receipt to that resolved commit.

This prevents a cross-surface race where one provider surface returns a newer state and another returns a stale state for the moving branch.

## Verified live execution

GitHub Actions run **196** passed on commit:

\`48301ce6263f93c4d4e7113828436f346a25870e7\`

The runtime:

- resolved \`main\` to commit \`48301ce...\`,
- invoked the Contents API using that commit,
- invoked Raw Content using the same commit,
- matched both byte streams,
- recomputed the Git blob identity,
- matched the provider blob SHA,
- verified receipt integrity and exact resource binding,
- passed receipt-tamper tests.

The durable receipt is stored in \`experiments/043c/result.json\`.

## Preserved failures

### Run 186 — TEST_FIXTURE_FAILURE

A unit fixture encoded the wrong text and blocked the first live-runtime attempt.

It decoded to \`MORPSS-043C\`, not \`MORPHS-043C\`.

It was corrected and revalidated.

### Run 194 — EXTERNAL_CONSISTENCY_FAILURE / TOCTOU

The adapter previously read both surfaces using the moving \`main\` ref.

During one live invocation:

- Contents API returned SHA-256 \`b1d693...\` and blob \`3c0eb3...\`.
- Raw \`main\` returned SHA-256 \`2d7fa9...\`, which matched the previous observed README state.

The correct result was **DEFER**.

The repair was not a retry. The protocol was changed so that the branch ref is first resolved to an immutable commit and both reads use that commit.

Run 196 then passed with byte-identical content and matching Git blob identity.

## Verification rule

The live observation is VERIFIED only when:

1. the runtime invocation returns successfully,
2. the requested ref resolves to a concrete commit,
3. the contents response is a file,
4. the raw response is read at the same resolved commit,
5. both byte streams match,
6. Git blob identity matches,
7. the invocation receipt is complete and hash-bound,
8. receipt/resource binding is exact,
9. receipt tampering tests reject modified identity/hash fields.

## Epistemic limits

Established within this scope:

\`MORPHS runtime -> real GitHub read-only provider\`

Still OPEN:

- provider-independent verification
- mutation through the MORPHS runtime
- ambiguous network outcome handling
- irreversible effects
- rollback
- distributed transaction semantics
- host capability-registry integration
