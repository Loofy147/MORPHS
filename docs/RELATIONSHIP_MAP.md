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

043: read-only protocol boundary + host-captured observation
043b: mutation protocol hardening + host-captured reversible canary
043c: real MORPHS runtime read-only provider adapter

The external path now has an explicit evidence chain:

deterministic protocol semantics
-> host-captured external evidence
-> MORPHS runtime invocation
-> injected host capability binding
-> immutable ref resolution
-> same-commit independent observation
-> Git identity verification
-> persisted receipt
-> trusted run/head revalidation
-> provider-independent verification (OPEN)

## 3. Relationship types

CAUSAL DEPENDENCY
One change requires a prerequisite.

EVIDENCE DEPENDENCY
A conclusion depends on an independent observation.

AUTHORITY DEPENDENCY
An action requires host permission.

RECEIPT DEPENDENCY
An external invocation must retain enough immutable information to bind the observed result to the actual invocation.

Example:
invocation id + execution surface + run/head + capability + resolved commit + request URLs + timestamps + response hashes -> receipt integrity.

REGISTRY BINDING
A runtime invocation must resolve through an explicit host capability registry.

Stronger experimental rule:
descriptor A + invoker B -> reject.

REFERENCE DEPENDENCY
A moving branch/tag ref is not sufficient for cross-surface verification when the external state can change during the observation window.

Rule:
resolve moving ref -> immutable commit -> bind all verification surfaces to that commit.

PERSISTENCE DEPENDENCY
Runtime evidence is not complete when a receipt is merely printed.

Rule:
invoke -> persist -> reread -> revalidate against trusted run/head -> artifact upload

Artifact metadata proves upload existence and digest; it does not establish cryptographic authenticity of receipt contents.

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

## 7. Dependency relation

Dependency failure must propagate through the task graph.

Example:
DB unavailable -> schema check unavailable -> application mutation blocked -> alternative plan or defer.

## 8. Unknown mutation outcome

MUTATION -> UNKNOWN_EXTERNAL_OUTCOME -> do not blindly retry -> observe current state -> classify

043b verifies containment deterministically. A live ambiguous network outcome remains OPEN.

## 9. Verification relation

External execution increases the required independence of verification.

intent -> action -> provider result -> receipt -> independent read -> identity/postcondition -> dependency check -> convergence decision

A provider success response is not equivalent to external equilibrium.

043 establishes protocol semantics and host-captured read evidence.

043b establishes hardened mutation protocol semantics and host-captured reversible canary evidence.

043c establishes actual MORPHS runtime invocation of a real GitHub read, exact-commit cross-surface binding, injected host registry, bound invoker enforcement, Git blob identity binding, freshness, persisted receipt revalidation, and trusted CI provenance binding.

The latest replay regression establishes an additional rule:

receipt self-consistency != receipt authenticity.

A receipt can be internally self-consistent after malicious recomputation, so trusted external provenance must anchor replay detection.

Provider-independent verification and cryptographic receipt authenticity remain OPEN.

## 10. Current architecture frontier

028-035 adaptive machinery
036-038 protected verification
039 protocol grounding
040 reversible state transitions
041 external-world reconciliation
042 dependency cascade propagation and partial external state
043 read-only external protocol boundary
043b mutation protocol integrity + host-captured reversible canary
043c real MORPHS runtime read-only provider adapter with immutable reference binding, injected host registry, and trusted receipt provenance

Next unresolved dimensions:
- provider-independent verification
- cryptographic receipt authenticity
- controlled ambiguous runtime outcomes
- runtime mutation through the bounded adapter
- stronger post-response freshness semantics
- irreversible side effects
- provider substitution under contract equivalence
- adversarial world-state reporting
- long-lived drift and re-equilibration
- distributed transaction semantics
- production-grade capability registry/isolation
