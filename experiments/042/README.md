# Experiment 042 — Dependency Cascades and Partial Failure

## Question

Can MORPHS preserve dependency semantics when a failure blocks a downstream branch, while also distinguishing a partial external mutation from a fully blocked reconciliation?

## Protocol

observe -> topological dependency order -> authorized mutation -> classify BLOCKED/PARTIAL/EQUILIBRATED -> preserve transition trace

## Cases

- Healthy graph: db -> api -> app and cache -> app converge in dependency order.
- Dependency cascade: unavailable db blocks api and then app; the system remains BLOCKED.
- Partial external failure: db and api converge, app mutation fails externally, leaving observable partial state.
- Authorization failure: no mutation bypasses missing authority.

## Key distinction

BLOCKED means the required mutation path could not safely proceed.

PARTIAL means some external mutations happened before another transition failed. The partial state must be observed and recorded before any recovery or rollback decision.

## Epistemic status

EXPERIMENTALLY_SUPPORTED

Scope: deterministic multi-resource external-world simulator.

Limitation: dependencies and failure injection are deterministic and host-specified. This does not establish safe orchestration of arbitrary distributed systems, transactions, or irreversible effects.

## Relationship

041 external equilibrium
-> 042 dependency propagation and partial external state
-> future real external runtime transfer
