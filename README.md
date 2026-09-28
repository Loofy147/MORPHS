# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiments 033-035 are repository-verified by GitHub Actions run 59.

Experiment 037 established independent verifier diversity and safe DEFER on verifier disagreement.

Experiment 042 is the current native research frontier:

> MORPH can distinguish dependency-blocked external reconciliation from partial external mutation, preserving downstream cascade state and transition evidence rather than collapsing both into a generic failure.

Epistemic state: EXPERIMENTALLY_SUPPORTED

Scope: deterministic multi-resource external-world reconciliation simulator built on the protocol-grounding, verification, and reversible-state boundaries.

This does not establish unrestricted automated root-cause identification. The audit contract, intervention range, verifier implementations, and protected authority remain supplied by the host.

### Verification status

- Experiment 036: GitHub Actions run 68 — verified
- Experiment 037: GitHub Actions run 75 — verified
- Experiment 038: GitHub Actions run 88 — verified (local compile + 7 tests also passed)
- Experiment 039: GitHub Actions run 103 — verified (compile + pytest + Experiments 028-039 all passed)
- Experiment 040: GitHub Actions run 123 — verified
- Experiment 041: GitHub Actions run 133 — verified
- Experiment 042: GitHub Actions run 148 — verified (compile + pytest + Experiments 028-042 all passed)

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

The full construction and evidence path is documented in docs/RESEARCH_PATHS.md.

Historical experiments 001-027 remain part of MORPH's lineage and are not being rewritten to fit the native repository experiments.
