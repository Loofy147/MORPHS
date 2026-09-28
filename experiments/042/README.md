# Experiment 042 — Dependency Cascades and Partial Failure

## Question

Can MORPHS preserve dependency semantics when a failure blocks a downstream branch, while also distinguishing a partial external mutation from a fully blocked reconciliation?

## Protocol

observe -> topological dependency order -> authorized mutation -> classify BLOCKED/PARTIAL/EQUILIBRATED -> preserve transition trace

## Cases

- Healthy graph: db -> api -> app and cache -> app converge in dependency order.
- Dependency cascade: unavailable db blocks api and then app, while the independent cache branch may still progress. Therefore the affected branch is BLOCKED but the global reconciliation may be PARTIAL.
- Partial external failure: db and api converge, app mutation fails externally, leaving observable partial state.
- Authorization failure: no mutation bypasses missing authority.

## Key distinction

BLOCKED is a scope-specific state: the affected dependency branch cannot safely proceed.

PARTIAL is a reconciliation-level state: some independent branches progressed or some mutations occurred while other branches remain blocked or failed. The partial state must be observed and recorded before recovery or rollback.

## Epistemic status

EXPERIMENTALLY_SUPPORTED

Scope: deterministic multi-resource external-world simulator.

Limitation: dependencies and failure injection are deterministic and host-specified. This does not establish safe orchestration of arbitrary distributed systems, transactions, or irreversible effects.

## Relationship

041 external equilibrium
-> 042 dependency propagation and partial external state
-> future real external runtime transfer


## Preserved engineering failure

Run 137 initially failed because the aggregate test assumed an upstream dependency failure would make the entire reconciliation BLOCKED. The CI evidence showed the cache branch was independent, so it legitimately progressed while the db-dependent api/app branch was blocked. Run 144 applied a first classification repair, then the final repair refined the model to distinguish branch-level blocking from global PARTIAL state.
