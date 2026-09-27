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

Experiment 032 is the latest native experiment.

Its claim is:

> MORPH can induce a reusable constructor from black-box traces and promote that constructor into the active surface language, then reuse it under unseen bindings and downstream transfer gates.

Epistemic state: **EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator with black-box numeric traces.

This does **not** establish unrestricted invention of primitive mathematical operators or self-modification of an arbitrary runtime. The constructor-mutation meta-language remains supplied by the experiment.

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
```

The repository is intentionally small. Historical experiments 001-027 remain part of MORPH's lineage and will be normalized as structured records rather than copied blindly.
