# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiments 033-035 are historical repository experiments.

The current external-mutation frontier is 043b:

> The deterministic MORPHS mutation protocol requires exact state/content identity, capability-bound authorization, independent postcondition verification, unknown-outcome containment, and rollback revalidation.

Epistemic state: EXPERIMENTALLY_SUPPORTED for the deterministic protocol scope.

A separate host-side GitHub canary mutation and rollback is recorded as HOST_CAPTURED_EXTERNAL evidence.

The current repository evidence does NOT establish that the MORPHS runtime itself invoked GitHub mutation.

### Verification status

The authoritative verification source is GitHub Actions on the current main HEAD.

Historical runs remain evidence of prior states:
- Experiment 042: run 148
- Experiment 043: prior full-regression run 168
- Experiment 043b: prior full-regression run 168

After the audit corrections, the current main HEAD must pass the full 028-043b workflow before the corrected claims are considered revalidated.

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

The full construction and evidence path is documented in docs/RESEARCH_PATHS.md.

Historical experiments 001-027 remain part of MORPH's lineage and are not being rewritten to fit the native repository experiments.
