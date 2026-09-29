# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiments 033-035 are repository-verified by GitHub Actions run 59.

Experiment 037 established independent verifier diversity and safe DEFER on verifier disagreement.

Experiment 043b is the current research frontier for the external-mutation protocol:

> The deterministic MORPHS mutation protocol requires exact state/content identity, capability-bound authorization, independent postcondition verification, unknown-outcome containment, and rollback revalidation.

Epistemic state: EXPERIMENTALLY_SUPPORTED

Scope: deterministic mutation protocol model. A separate host-side GitHub canary mutation and rollback is recorded as external evidence.

The current repository evidence does NOT establish that the MORPHS runtime itself invoked GitHub mutation.

### Verification status

- Experiment 036: GitHub Actions run 68 — verified
- Experiment 037: GitHub Actions run 75 — verified
- Experiment 038: GitHub Actions run 88 — verified
- Experiment 039: repository-verified protocol grounding
- Experiment 040: repository-verified reversible adaptation
- Experiment 041: repository-verified external-world equilibrium
- Experiment 042: GitHub Actions run 148 — verified
- Experiment 043: revalidation pending after evidence-boundary hardening
- Experiment 043b: revalidation pending after adversarial identity/authority hardening

Prior green CI runs remain historical evidence; they do not certify the newly modified HEAD until the new HEAD passes.

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
