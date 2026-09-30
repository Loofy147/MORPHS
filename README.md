# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiment 043c is the current external-runtime frontier:

> The MORPHS Python runtime can invoke a real public GitHub read operation through a bounded adapter, produce a hash-bound invocation receipt, independently read the same immutable commit through a second GitHub surface, and verify content plus Git blob identity before classifying the observation.

Epistemic state: EXPERIMENTALLY_SUPPORTED

Scope: one real read-only GitHub runtime adapter invocation for \`Loofy147/MORPHS@main:README.md\`, with \`main\` resolved to an exact commit before cross-surface verification.

This does NOT establish provider-independent verification, mutation through the MORPHS runtime, ambiguous network outcome handling, rollback, distributed transactions, or unrestricted capability-registry integration.

The 043b mutation canary remains HOST_CAPTURED_EXTERNAL evidence; the MORPHS runtime mutation path remains OPEN.

### Verification status

The authoritative verification source is GitHub Actions on the current main HEAD.

Current external-runtime evidence:
- 043c: run 196 — verified
- 043c durable receipt: stored in \`experiments/043c/result.json\`

Preserved negative evidence:
- run 186: TEST_FIXTURE_FAILURE
- run 194: EXTERNAL_CONSISTENCY_FAILURE / TOCTOU; repaired by exact-commit pinning
- run 196: revalidation success

Prior green runs are historical evidence; the current main HEAD must pass its own full workflow before any new claim is promoted.

## Development rule

No important claim may disappear into context.

Every material experiment should end in one of:
- supported evidence
- contradiction
- refinement
- rejected hypothesis
- explicitly OPEN uncertainty

## Verification

    python -m pytest -q
    python -m compileall morph_core tests
    python -m morph_core.experiment028
    python -m morph_core.experiment029
    python -m morph_core.experiment030
    python -m morph_core.experiment031
    python -m morph_core.experiment032
    python -m morph_core.experiment033
    python -m morph_core.experiment034
    python -m morph_core.experiment035
    python -m morph_core.experiment036
    python -m morph_core.experiment037
    python -m morph_core.experiment038
    python -m morph_core.experiment039
    python -m morph_core.experiment040
    python -m morph_core.experiment041
    python -m morph_core.experiment042
    python -m morph_core.experiment043
    python -m morph_core.experiment043b
    python -m morph_core.experiment043c

The full construction and evidence path is documented in docs/RESEARCH_PATHS.md.

Historical experiments 001-027 remain part of MORPH's lineage and are not being rewritten to fit the native repository experiments.
