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

Experiments 033-035 extend the current native frontier.

Their claims are currently treated separately:

- **033 — EXPERIMENTALLY_SUPPORTED candidate pending final CI closure:** MORPH can detect a resource-induced representation bottleneck and introduce a generic binding mechanism that changes the active constructor language.
- **034 — EXPERIMENTALLY_SUPPORTED candidate pending final CI closure:** MORPH can defer, reuse, or evolve under explicit budget and mutation-risk gates.
- **035 — EXPERIMENTALLY_SUPPORTED candidate pending final CI closure:** MORPH can revalidate learned schema memory under rebinding and semantic drift, preserve contradicted memory historically, and require revalidation before replacement.

These remain deterministic simulator claims. They do not establish unrestricted self-modification or unrestricted invention of primitive semantics.

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

The repository is intentionally small. Historical experiments 001-027 remain part of MORPH's lineage and will be normalized as structured records rather than copied blindly.
