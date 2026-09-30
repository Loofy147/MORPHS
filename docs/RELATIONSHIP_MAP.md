# MORPHS relationship map

## 1. System construction graph

MORPHS is one bounded ecology, not a collection of independent experiments.

HOST CONSTITUTION
  -> authority / execution limits / verifier integrity / audit integrity / promotion rules
  -> PROTOCOL LAYER
  -> states / capability contracts / evidence / recovery / provenance / durable events
  -> ADAPTIVE ECOLOGY
  -> rules / operators / memory / workflows / verifier proposals / investigation
  -> EXTERNAL WORLD
  -> resources / dependencies / versions / availability / drift / side effects / unknown outcomes

The external world is an observed, partially controllable environment, not an internal memory owned by MORPHS.

## 2. Experiment relationships

028-035: adaptive substrate
028 constitution constraints
-> 029 rule-language induction
-> 030 operator evolution
-> 031 reusable schemas
-> 032 constructor vocabulary
-> 033 meta-language abstraction
-> 034 budget-aware mutation
-> 035 memory revalidation

036-038: protected verification
036 shadow verifier
-> 037 independent verifier diversity
-> 038 disagreement investigation

039: protocol grounding
known fact -> constraint
unknown -> experiment
contradiction -> preserve + investigate
known failure -> regression protection

040: reversible adaptation
propose -> verify -> promote -> active state -> revalidate -> rollback or block -> preserve lineage -> audit

041: external-world equilibrium
042: dependency cascades and partial external failure
043: read-only protocol boundary + host-captured observation
043b: mutation protocol hardening + host-captured reversible canary
043c: real MORPHS runtime read-only provider adapter

The external path now has an explicit evidence chain:

deterministic protocol semantics
-> host-captured external evidence
-> MORPHS runtime invocation
-> durable invocation receipt
-> independent same-provider observation
-> identity verification
-> provider-independent verification (OPEN)

## 3. Relationship types

CAUSAL DEPENDENCY
One change requires a prerequisite.
Example: application version -> database schema compatibility.

EVIDENCE DEPENDENCY
A conclusion depends on an independent observation.
Example: deployment result -> external postcondition.

AUTHORITY DEPENDENCY
An action requires host permission.
Example: mutation -> authority gate.

TEMPORAL DEPENDENCY
A later action depends on an earlier state transition.
Example: rollback -> prior promoted version.

FRESHNESS DEPENDENCY
A decision becomes invalid when its observation becomes stale.
Example: cached external state -> re-observe.

LINEAGE DEPENDENCY
A derived artifact retains the parent that produced it.
Example: v2 -> parent v1.

RECONCILIATION DEPENDENCY
The plan must be regenerated when observed external state differs from expected state.
Example: desired != observed -> replan.

IDENTITY DEPENDENCY
Semantic state labels are insufficient when external content identity can change.
Example: same logical state + different blob -> DEFER.

RECEIPT DEPENDENCY
An external invocation must retain enough immutable information to bind the observed result to the actual invocation.
Example: invocation id + request URL + timestamp + response hash -> receipt integrity.

## 4. External-world model

CONTROLLED STATE
MORPHS may mutate it when authorized.

OBSERVABLE STATE
MORPHS can read it but cannot directly control it.

DERIVED STATE
MORPHS infers it from observations and must not treat the inference as direct observation.

UNKNOWN STATE
Neither current value nor mutation outcome is established.

Unknown external state is a first-class state.

## 5. Equilibrium definition

For MORPHS, external equilibrium means:
desired state == verified observed state
AND required dependencies are satisfied
AND no unresolved authority condition exists
AND no material contradiction remains
AND observation is fresh enough for the decision.

Equilibrium is local and scoped. It does not mean permanent external stability.

## 6. Drift relation

EQUILIBRIUM -> external change -> DRIFT -> observe -> compare -> reconcile or block

A previously verified state can become stale without the historical evidence becoming false.

This is the external-world analogue of Experiment 035 memory drift.

## 7. Dependency relation

Dependency failure must propagate through the task graph.

Example:
DB unavailable -> schema check unavailable -> application mutation blocked -> alternative plan or defer.

## 8. Unknown mutation outcome

MUTATION -> UNKNOWN_EXTERNAL_OUTCOME -> do not blindly retry -> observe current state -> classify

Possible classification:
- already applied
- not applied
- partially applied
- unresolved

043b requires both semantic state and content identity to resolve known/unknown branches safely.

A live ambiguous provider outcome remains OPEN.

## 9. Verification relation

External execution increases the required independence of verification.

intent -> action -> provider result -> receipt -> independent read -> identity/postcondition -> dependency check -> convergence decision

A provider success response is not equivalent to external equilibrium.

043 establishes protocol semantics and host-captured read evidence.

043b establishes hardened mutation protocol semantics and host-captured reversible canary evidence.

043c establishes actual MORPHS runtime invocation of a real GitHub read, receipt integrity, same-provider independent observation, and Git blob identity binding.

Provider-independent verification remains OPEN.

## 10. Current architecture frontier

028-035 adaptive machinery
036-038 protected verification
039 protocol grounding
040 reversible state transitions
041 external-world reconciliation
042 dependency cascade propagation and partial external state
043 read-only external protocol boundary
043b mutation protocol integrity + host-captured reversible canary
043c real MORPHS runtime read-only provider adapter

Next unresolved dimensions:
- host capability-registry integration
- provider-independent verification
- runtime mutation through the bounded adapter
- real ambiguous mutation outcomes
- irreversible side effects
- provider substitution under contract equivalence
- adversarial world-state reporting
- long-lived drift and re-equilibration
- distributed transaction semantics
