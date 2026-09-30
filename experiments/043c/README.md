# Experiment 043c — Real Runtime Adapter and Invocation Receipt

## Research question

Can MORPHS itself invoke a real external provider through a bounded runtime adapter, retain an invocation receipt, independently read the same resource through a second provider surface, and verify content plus provider identity before classifying the observation?

## Verified scope

043c is read-only.

The MORPHS Python runtime now:

1. resolves a moving ref to an exact commit,
2. binds the capability through an explicit host registry,
3. requires a bound invoker when the registry enforces adapter binding,
4. invokes GitHub Contents API at the exact commit,
5. invokes GitHub Raw at the same exact commit,
6. verifies freshness and byte equality,
7. verifies Git blob identity,
8. persists the invocation receipt,
9. re-reads and revalidates the persisted receipt against run/head identity,
10. uploads the receipt as a GitHub Actions artifact.

## Verification

GitHub Actions **Run 223** passed on HEAD:

`2f7c4da58ab5cd6922c745705a2f5d7512987b11`

The full sequence passed:

`Compile -> pytest -> Experiments 028-043c -> receipt persistence -> artifact upload`

The runtime receipt was bound to:

- execution surface: `MORPHS_PYTHON_RUNTIME`
- CI run: `36734688924`
- CI head: `2f7c4da58ab5cd6922c745705a2f5d7512987b11`
- capability: `github.repository.read_file`
- scope: `Loofy147/MORPHS@main:README.md`

The receipt file was revalidated before upload:

- file SHA-256: `9e43eebb...`
- self-consistent: true
- run match: true
- HEAD match: true

GitHub Actions artifact:

- artifact ID: `11106886183`
- digest: `sha256:548b44ebab35db82a6fc857cd523ce8d3a16053eb7da9ec6d51599b92fd08ee2`
- size: 862 bytes

Artifact existence and digest are confirmed from GitHub Actions metadata. The current connector cannot independently download the ZIP bytes for a second content-level inspection.

## Adversarial hardening

The audit found and corrected:

- moving-ref TOCTOU across two provider surfaces,
- automatic local-registry creation that bypassed the host boundary,
- descriptor/invoker mismatch at registry binding,
- stale and incorrect test assumptions,
- missing CI provenance in the receipt,
- persisted-receipt reconstruction failure,
- fixture and test-source failures.

The registry now rejects:

`descriptor A + invoker B`

when bound-invoker enforcement is enabled.

## Evidence boundary

`RUNTIME_OBSERVED` is justified for this exact read-only GitHub scope.

It is not equivalent to:

- provider-independent verification,
- cryptographic receipt authenticity,
- arbitrary external orchestration,
- runtime mutation,
- ambiguous outcome safety,
- rollback correctness.

## Remaining OPEN boundaries

- provider-independent verification
- cryptographic receipt authenticity
- real ambiguous network outcome handling
- mutation through the MORPHS runtime
- irreversible effects
- rollback
- distributed transaction semantics
- production-grade capability registry
- provider substitution under contract equivalence

Runtime mutation remains outside the promotion boundary until a stronger independent-verification gate is established.
