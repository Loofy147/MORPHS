# MORPHS relationship map

## 2. Experiment relationships

043: read-only protocol boundary + host-captured observation
043b: mutation protocol hardening + host-captured reversible canary
043c: real MORPHS runtime read-only provider adapter

The external path now has an explicit evidence chain:

deterministic protocol semantics
-> host-captured external evidence
-> MORPHS runtime invocation
-> ref-resolution receipt
-> same-commit independent observation
-> identity verification
-> provider-independent verification (OPEN)

## 3. Relationship types

RECEIPT DEPENDENCY
An external invocation must retain enough immutable information to bind the observed result to the actual invocation.

Example:
invocation id + resolved commit + request URL + timestamp + response hash -> receipt integrity.

REFERENCE DEPENDENCY
A moving branch/tag ref is not sufficient for cross-surface verification when the external state can change during the observation window.

Rule:
resolve moving ref -> immutable commit -> bind all verification surfaces to that commit.

## 9. Verification relation

External execution increases the required independence of verification.

intent -> action -> provider result -> receipt -> independent read -> identity/postcondition -> dependency check -> convergence decision

A provider success response is not equivalent to external equilibrium.

043 establishes protocol semantics and host-captured read evidence.

043b establishes hardened mutation protocol semantics and host-captured reversible canary evidence.

043c establishes actual MORPHS runtime invocation of a real GitHub read, receipt integrity, exact-commit cross-surface binding, same-provider independent observation, and Git blob identity binding.

Run 194 demonstrated that using a moving branch ref could produce cross-surface disagreement; the correct classification was DEFER and the repair was immutable commit binding.

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
043c real MORPHS runtime read-only provider adapter with immutable reference binding

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
