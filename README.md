# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

Conversation notes and generated snapshots are not authoritative.

## Current boundary

Experiments 033-035 are repository-verified by GitHub Actions run 59.

Experiment 036 is the latest native frontier:

> MORPH can propose a shadow verifier that matches an immutable host verifier across training, protected holdout, and anti-gaming evidence, while remaining unable to grant itself verifier authority.

Epistemic state: **EXPERIMENTALLY_SUPPORTED locally; CI PENDING**

Scope: deterministic symbolic verifier-evolution simulator.

This does **not** establish unrestricted self-modification of verifier semantics. The candidate grammar and immutable host kernel are supplied.

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
python -m morph_core.experiment036
```

Historical experiments 001-027 remain part of MORPH's lineage and are not being rewritten to fit the native repository experiments.
