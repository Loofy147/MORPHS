# Experiment 043c — Real Runtime Adapter and Invocation Receipt

## Research question

Can MORPHS itself invoke a real external provider through a bounded runtime adapter, retain an invocation receipt, independently read the same immutable commit through a second provider surface, and verify content plus provider identity before classifying the observation?

## Verified scope

043c is read-only.

The MORPHS Python runtime:

1. resolves a moving ref to an exact commit,
2. receives an explicitly injected host capability registry,
3. requires the registry to bind the adapter invoker to the descriptor,
4. invokes GitHub Contents API at the exact commit,
5. invokes GitHub Raw at the same exact commit,
6. verifies freshness and byte equality,
7. verifies Git blob identity,
8. persists the invocation receipt,
9. revalidates the persisted receipt against trusted GitHub Actions run/head identifiers,
10. uploads the receipt as a GitHub Actions artifact.

The GitHub Actions job is constrained to `contents: read`.

## Verification

GitHub Actions **Run 237** passed on HEAD:

`c47674a2f4de7e16054cdee4f3771cc6ddfa325f`

The full sequence passed:

`Compile -> pytest -> Experiments 028-043c -> receipt persistence -> artifact upload`

The live runtime invocation produced:

- execution surface: `MORPHS_PYTHON_RUNTIME`
- CI run: `37045789898`
- CI head: `c47674a2f4de7e16054cdee4f3771cc6ddfa325f`
- capability: `github.repository.read_file`
- scope: `Loofy147/MORPHS@main:README.md`
- resolved commit: `c47674a2f4de7e16054cdee4f3771cc6ddfa325f`
- Git blob identity: `e64610b26ba4578e7339b34652b53a1d148bc116`
- Contents/Raw content SHA-256: `9a91ab924a4ed60327e3365340e8862170be78a10118d28078bf199ba6d5c702`

Receipt persistence:

- file SHA-256: `07eda1fb1fbbad4e60aaaeea9482c0c0d015d1af38c2fb0d84a016b94ffcc05a`
- self-consistent: true
- run match: true
- HEAD match: true
- trusted anchor: `GITHUB_RUN_ID + GITHUB_SHA`

Artifact:

- ID: `11244079102`
- digest: `sha256:1d82a92d655bf267b4cd8fd331e9f3a4388754710d8b9e19ed3e6d75db3eed25`
- size: 865 bytes

## Adversarial hardening

The research path preserved and repaired:

- moving-ref TOCTOU between Contents and Raw,
- registry/invoker mismatch,
- registry-bypass assumptions,
- CI provenance assumptions,
- persisted-receipt reconstruction,
- broader-than-needed CI token permissions,
- replay of a receipt with recomputed self-hash and forged run/head identifiers.

The final replay regression confirms that self-consistency alone is insufficient: trusted CI provenance is required for persisted-receipt revalidation.

## Evidence boundary

Runtime invocation is `VERIFIED` for this exact read-only GitHub scope.

This does not establish:

- provider-independent verification,
- cryptographic receipt authenticity,
- arbitrary external orchestration,
- runtime mutation,
- ambiguous network outcome safety,
- rollback correctness,
- distributed transaction semantics,
- production-grade capability isolation.

The live 043b mutation remains HOST_CAPTURED_EXTERNAL evidence; the runtime mutation path remains OPEN.

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
- stronger freshness semantics

Runtime mutation remains outside the promotion boundary until a stronger independent-verification gate is established.
