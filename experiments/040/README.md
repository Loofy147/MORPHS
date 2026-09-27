# Experiment 040 — Reversible Adaptation

## Question

Can MORPHS promote an adaptive version and later roll it back without deleting lineage, bypassing authority, or reactivating a stale version without revalidation?

## Protocol

propose → verify → promote → revalidate rollback target → rollback or block → preserve lineage → audit

## Required properties

1. retain the promoted version in history;
2. require host authorization;
3. revalidate the rollback target against the current environment;
4. append a rollback transition rather than erase history;
5. block when current evidence no longer supports the target.

## Cases

Valid promotion and rollback: v0 → v1 is verified and promoted; v0 is then revalidated under the stable environment and restored as active without deleting v1.

Unauthorized transition: a promotion attempt without host authorization is blocked.

Environment drift: the rollback target is tested under a changed environment. Revalidation fails and the rollback is blocked.

Audit tampering: an attempted audit deletion changes the event count and becomes observable.

## Epistemic status

EXPERIMENTALLY_SUPPORTED

Scope: deterministic versioned-adaptation simulator.

Limitation: version graph, authorization, revalidation predicate, and audit mechanism are host-supplied. This does not establish rollback correctness for arbitrary external side effects or irreversible systems.

## Research value

040 changes adaptation from promotion-only to promotion followed by revalidation-aware rollback or blocking.

A blocked rollback is preserved as safety-relevant evidence, not hidden as an implementation embarrassment.
