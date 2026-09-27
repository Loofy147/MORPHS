# Experiment 035 — Memory Drift and Constructor Revalidation

## Question

Can MORPH reuse learned schemas across valid rebinding while detecting semantic drift, preserving contradicted memory historically, and requiring revalidation before replacement promotion?

## Verified result

GitHub Actions run 59 passed the complete regression.

- stable reuse: true
- rebound reuse: true
- old schema under drift: false
- drift transition: `contradicted`
- historical memory preserved: 1 entry
- replacement: `abs(s0-s1) <= 2`
- replacement revalidated: true
- decoy old-memory fit: false
- decoy candidate discovery: empty

## Repair history

The first implementation referenced a nonexistent assertion variable during result construction. The runtime state itself was already computed correctly.

The variable reference was corrected, after which 035 passed pytest and direct experiment execution in the full 033-035 regression.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic memory and bounded schema-discovery simulator.

Limitation: the discovery space is bounded to absolute-difference thresholds 0..3. This tests contradiction handling and revalidation, not open-ended memory invention.
