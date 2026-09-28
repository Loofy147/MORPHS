# Experiment 041 — External World Equilibrium

## Question

Can MORPHS carry its evidence, authority, dependency, freshness, and reconciliation rules across the boundary into an externally mutable world?

## Protocol

observe -> dependency check -> authorized reconciliation -> observe post-state -> convergence or drift -> re-observe

## Cases

### Initial reconciliation
The world starts with app-v1 and db-v1. Desired state is app-v2 with db-v2, and the application depends on the database. MORPHS reconciles the dependency first, then the application, and verifies the post-state from fresh observation.

### External drift
After convergence, the database is changed externally to db-v3. MORPHS must treat the previous equilibrium as stale and observe the mismatch rather than relying on historical memory.

### Dependency block
The database becomes unavailable. The application mutation is blocked because its dependency is not satisfied.

### Unknown mutation outcome
The provider returns an unknown mutation outcome. MORPHS must observe current external state before deciding whether another mutation is safe.

### Authorization block
The desired change exists but mutation authority is absent. The system remains out of equilibrium rather than bypassing authority.

## Equilibrium

Equilibrium means desired state equals verified observed state, required dependencies are satisfied, no unresolved authority condition remains, no material contradiction remains, and observation is fresh enough for the decision.

Equilibrium is local and scoped. It is not permanent control of the external world.

## Epistemic status

EXPERIMENTALLY_SUPPORTED

Scope: deterministic external-world reconciliation simulator.

Limitation: this does not establish safety for arbitrary external APIs, irreversible effects, network partitions, or adversarial state reporting.

## Relationship to prior experiments

035 memory revalidation
-> 038 disagreement investigation
-> 039 protocol grounding
-> 040 reversible adaptation
-> 041 external state reconciliation
