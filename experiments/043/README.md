# Experiment 043 — Real External Runtime Transfer

## Research question

Can MORPHS transfer its capability, authority, provenance, freshness, and independent-postcondition protocol across a real external provider boundary without treating provider success as world verification?

## Why this experiment exists

042 established dependency cascades and partial state in a deterministic external-world model.

043 is deliberately narrower. It crosses a **real provider boundary** using a read-only GitHub observation and checks whether the protocol survives the boundary:

discover capability
-> classify authority
-> bind resource
-> execute read
-> independently observe
-> verify postcondition
-> record provenance and freshness

This is a transfer experiment, not a claim of unrestricted external orchestration.

## Live boundary

Provider: GitHub

Repository: \`Loofy147/MORPHS\`

Operation: read \`README.md\` at \`main\`

Primary surface: repository contents

Independent surface: raw content

Authority: \`READ_ONLY\`

Side effects: none

The captured live observation matched across the two surfaces for the same repository/path/ref and was tied to the observed \`main\` commit and README blob identity.

## Deterministic regression cases

The experiment also tests the protocol against three controlled cases:

1. Clean transfer -> VERIFIED.
2. Provider output differs from the independent observation -> DEFER.
3. Observation exceeds the freshness budget -> DEFER.

The second case is the key safety test: a tool/provider response is not accepted as the external postcondition by itself.

## Epistemic status

\`EXPERIMENTALLY_SUPPORTED\`

Scope: one real read-only GitHub boundary plus deterministic protocol regression.

## What this does NOT establish

- provider-independent verification
- external mutation safety
- unknown mutation outcome handling in a real provider
- irreversible-effect safety
- distributed transaction semantics
- real rollback correctness
- provider substitution under contract equivalence
- adversarial external state reporting

Those remain OPEN.

## Preserved design rule

**Capability exists -> addressable -> invoked -> succeeded -> independently observed -> postcondition verified.**

The live observation demonstrates the transfer path through a real external surface. The deterministic cases protect the more important rule: external success is never silently upgraded into equilibrium.

## Next boundary

043b should test a narrowly scoped **authorized reversible mutation** with:

- explicit mutation authority
- pre-read
- idempotency check
- mutation
- independent post-read
- unknown-outcome containment
- rollback or compensating action
- preserved audit lineage

Mutation should remain a separate research step, not be smuggled into 043.
