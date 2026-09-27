# Experiment 035 — Memory Drift and Constructor Revalidation

## Question

Can MORPH reuse learned schemas across valid rebinding while detecting semantic drift, preserving the contradicted memory historically, and requiring revalidation before replacement promotion?

## Protocol

`reuse → shifted rebinding → contradiction → archive → rediscovery → revalidation → promotion`

The experiment includes a decoy environment where naive familiarity would be misleading.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic memory and bounded schema-discovery simulator.

The discovery space is intentionally bounded to absolute-difference thresholds 0..3.
