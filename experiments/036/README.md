# Experiment 036 — Verifier Shadow Evolution

## Challenge

Can MORPH propose a change to verifier logic without gaining verifier authority?

The rule is deliberately harsh:

> MORPH may propose; MORPH does not authorize.

A protected host kernel remains the source of promotion authority. Candidate verifiers are shadow policies only.

## Protocol

`black-box evidence traces → verifier proposal search → training fit → protected holdout → anti-gaming cases → promotion by immutable kernel`

The candidate language is deliberately small: conjunctions over observable evidence fields plus a zero-counterexample condition.

The learner is never given a field called "accept". It must reconstruct the protected acceptance boundary from labeled evidence.

## Verified result

- candidate space: 511
- promoted verifier:
  `train AND holdout AND transfer AND adversarial AND intervention AND lineage AND scope AND negative_control AND counterexamples == 0`
- training match: true
- holdout match: true
- anti-gaming match: true
- all four decoy verifiers rejected
- kernel version remained `kernel:v1`
- self-authority granted: false

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic verifier-evolution simulator.

Important limitation: the candidate grammar and immutable kernel are supplied. 036 tests shadow verifier evolution and preservation of verifier authority, not unrestricted self-modification of the verifier substrate.

## Research value

036 makes the authority boundary executable:

`proposal != authority`

A candidate verifier can become better evidence-backed without becoming the owner of the gate.

The next pressure point is harder: introduce **independent verifier diversity**, where MORPH must survive disagreement between two independently implemented verifiers rather than matching a single kernel.
