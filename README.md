# MORPHS

MORPH is an experimental software-ecology research system for studying how machine agents can discover capabilities, form hypotheses, test assumptions, manage memory, evolve policies, and govern their own learning under explicit evidence and execution constraints.

## Source of truth

This repository is the canonical source of truth for MORPH.

The repository records:
- runtime code and machine-readable experiment definitions
- experiment inputs, outputs, and verification evidence
- epistemic status of claims
- lineage of evolving rules, capabilities, memories, and theories
- rejected and superseded hypotheses

Conversation notes and generated zip snapshots are not authoritative.

## Current boundary

Experiment 030 is the latest native experiment.

Its claim is:

> MORPH can extend a machine-level rule language by selecting derived operators from a typed constructive substrate, then admitting them only after holdout, transfer, adversarial, and intervention evidence.

Epistemic state: **EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator only.

This does **not** establish unrestricted invention of mathematical primitives or real-world scientific discovery.

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
```

The repository is intentionally small. Historical experiments 001-027 remain part of MORPH's lineage and will be normalized as structured records rather than copied blindly.
