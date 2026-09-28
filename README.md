# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiments 033-035 are repository-verified by GitHub Actions run 59.

Experiment 037 established independent verifier diversity and safe DEFER on verifier disagreement.

Experiment 043b is the current native research frontier:

> MORPH can execute a narrowly authorized reversible mutation on a real GitHub boundary, verify the postcondition independently, contain unknown outcomes, and roll back only when the external state still matches the expected mutated state.

Epistemic state: EXPERIMENTALLY_SUPPORTED

Scope: one reversible text-file mutation on a dedicated GitHub branch plus deterministic protocol regressions.

This does not establish unrestricted automated root-cause identification, arbitrary external mutation safety, irreversible side-effect safety, distributed transaction semantics, or provider-independent mutation verification.

### Verification status

- Experiment 036: GitHub Actions run 68 — verified
- Experiment 037: GitHub Actions run 75 — verified
- Experiment 038: GitHub Actions run 88 — verified (local compile + 7 tests also passed)
- Experiment 039: GitHub Actions run 103 — verified (compile + pytest + Experiments 028-039 all passed)
- Experiment 040: GitHub Actions run 123 — verified
- Experiment 041: GitHub Actions run 133 — verified
- Experiment 042: GitHub Actions run 148 — verified (compile + pytest + Experiments 028-042 all passed)
- Experiment 043: GitHub Actions run 157 — verified (compile + pytest + Experiments 028-043 all passed)
- Experiment 043b: GitHub Actions run 164 — verified (compile + pytest + Experiments 028-043b all passed on the verified experiment branch head)

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
