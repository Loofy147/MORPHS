# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiments 033-035 are now repository-verified:

- **033 — EXPERIMENTALLY_SUPPORTED:** MORPH can detect a resource-induced representation bottleneck and extend the active constructor language with a generic binding mechanism that reduces representation cost while preserving transfer.
- **034 — EXPERIMENTALLY_SUPPORTED:** MORPH can reuse, evolve, or defer under explicit budget and mutation-risk gates rather than mutating by default.
- **035 — EXPERIMENTALLY_SUPPORTED:** MORPH can reuse schema memory across valid rebinding, detect semantic drift, preserve contradicted memory historically, and promote a replacement only after revalidation.

Scope for all three: deterministic symbolic simulators.

These experiments do **not** establish unrestricted self-modification, unrestricted invention of primitive semantics, or real-world scientific discovery.

## Evidence status

GitHub Actions run **59** is the final verified regression for the 033-035 burst.

- compile: success
- pytest: success
- Experiment 028: success
- Experiment 029: success
- Experiment 030: success
- Experiment 031: success
- Experiment 032: success
- Experiment 033: success
- Experiment 034: success
- Experiment 035: success

## Development rule

No important claim may disappear into context.

Every material experiment should end in one of:
- supported evidence
- contradiction
- refinement
- rejected hypothesis
- explicitly OPEN uncertainty

## Verification

```bash
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
```

Historical experiments 001-027 remain part of MORPH's lineage and are not being rewritten to fit the native repository experiments.
