# Experiment 037 — Independent Verifier Diversity

## Question

Can MORPH survive disagreement between independently implemented verifier kernels without choosing the verdict itself?

## Protocol

`candidate → verifier A/B agreement → clean promotion → fault injection → disagreement → DEFER`

The clean case uses two different implementations of the same protected acceptance contract.

The fault-injected verifier deliberately omits the negative-control condition.

When the independent verifiers disagree, the learner is not allowed to choose the result. Promotion becomes **DEFER**.

## Verified local result

- candidate matches clean verifier A: true
- candidate matches clean verifier B: true
- clean training agreement: true
- clean holdout agreement: true
- clean promotion: true
- injected verifier disagreement: true
- disagreement → DEFER: true
- candidate cannot override disagreement: true

## Epistemic status

**EXPERIMENTALLY_SUPPORTED locally; CI PENDING**

Scope: deterministic verifier-diversity simulator.

Important limitation: independent implementations are supplied. This tests the control response to verifier diversity and disagreement, not proof of independence for arbitrary future implementations.

## Research value

037 raises the verification bar from:

`one verifier says yes`

to:

`independent verifiers agree`

and explicitly treats disagreement as a first-class epistemic state rather than forcing a binary accept/reject choice.

## Next pressure point

The next challenge is to let the learner observe verifier disagreement as evidence and decide whether to investigate the **claim**, the **verifier**, or the **environment** without being allowed to erase the disagreement.
