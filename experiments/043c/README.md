# Experiment 043c — Real Runtime Adapter and Invocation Receipt

## Research question

Can MORPHS itself invoke a real external provider through a bounded runtime adapter, retain an invocation receipt, independently read the same immutable commit through a second provider surface, and verify content plus provider identity before classifying the observation?

## Verified scope

043c is read-only.

The MORPHS Python runtime:

1. resolves a moving ref to an exact commit,
2. receives an explicitly injected host capability registry,
3. requires the registry to bind the adapter invoker to the descriptor,
4. receives the host-injected GitHub token,
5. invokes GitHub Contents API at the exact commit,
6. invokes GitHub Raw at the same exact commit,
7. verifies freshness and byte equality,
8. verifies Git blob identity,
9. persists the invocation receipt,
10. revalidates the persisted receipt against trusted GitHub Actions run/head identifiers,
11. uploads the receipt as a GitHub Actions artifact.

The workflow job is constrained to `contents: read`. The authenticated credential is used by the Contents/ref-resolution requests. The Raw surface is a public read surface and is intentionally not authenticated.

## Verification

GitHub Actions **Run 248** passed on HEAD:

`b1b9dca15847d8c4d629e246c4d449321f724fc8`

The full sequence passed:

`Compile -> pytest -> Experiments 028-043c -> live runtime adapter -> receipt persistence -> artifact upload`

The live runtime invocation produced:

- execution surface: `MORPHS_PYTHON_RUNTIME`
- CI run: `37648244782`
- CI head: `b1b9dca15847d8c4d629e246c4d449321f724fc8`
- capability: `github.repository.read_file`
- scope: `Loofy147/MORPHS@main:README.md`
- resolved commit: `b1b9dca15847d8c4d629e246c4d449321f724fc8`
- Git blob identity: `e1d9d5959f8d80939d039be66743ed35f1896927`
- Contents/Raw content SHA-256: `a14f177c60aa85e138c70af87117b49326eb47f7b9ae165856ec0d47698f7979`
- host credential mode: `GITHUB_TOKEN`
- trusted CI context: true

Receipt persistence:

- file SHA-256: `9b5cfaa6ad87c79bd06982df3b39e3d2a0abea4387c2f3404b0ee145f3e1b2c7`
- self-consistent: true
- run match: true
- HEAD match: true
- trusted anchor: `GITHUB_RUN_ID + GITHUB_SHA`

Artifact:

- ID: `11495716044`
- digest: `sha256:f1bbb6ebd1011a1093731fddd00b31ab5e2a24202796b5b628a9e343d4b9970c`
- size: 868 bytes

## Adversarial hardening

The research path preserved and repaired:

- moving-ref TOCTOU between Contents and Raw,
- registry/invoker mismatch,
- registry-bypass assumptions,
- CI provenance assumptions,
- persisted-receipt reconstruction,
- broader-than-needed CI token permissions,
- replay of a receipt with recomputed self-hash and forged run/head identifiers,
- premature freshness timestamps,
- local execution being promoted using synthetic identifiers,
- missing provider credential propagation,
- stale test fixtures after credential hardening.

These failures remain evidence.

## Evidence boundary

Runtime invocation is `VERIFIED` for this exact read-only GitHub scope.

The claim is deliberately narrower than "external orchestration":

**MORPHS runtime -> bounded host registry -> authenticated read-only GitHub invocation -> immutable-commit cross-surface verification -> persisted/revalidated receipt.**

This does not establish:

- provider-independent verification,
- cryptographic receipt authenticity,
- independent attestation of the CI run,
- arbitrary external orchestration,
- runtime mutation,
- ambiguous network outcome safety,
- rollback correctness,
- distributed transaction semantics,
- production-grade capability isolation.

## Remaining OPEN boundaries

- provider-independent verification
- cryptographic receipt authenticity
- independent CI-run attestation
- real ambiguous network outcome handling
- mutation through the MORPHS runtime
- irreversible effects
- rollback
- distributed transaction semantics
- production-grade capability registry
- provider substitution under contract equivalence
- stronger post-response freshness semantics

Runtime mutation remains outside the promotion boundary until a stronger independent-verification gate is established.
