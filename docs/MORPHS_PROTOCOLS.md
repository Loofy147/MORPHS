# MORPHS Native Protocols
## Host-Grounded Adaptive Ecology Protocol v1.0

## 0. Purpose

This document specializes the portable orchestration baseline for MORPHS.
It is a protocol and architecture contract, not evidence that MORPHS already implements every capability described here.

Core rule:

Give MORPHS known facts and high-level constraints as explicit protocol inputs. Do not make MORPHS rediscover host facts that are already part of the constitution. Reserve experimentation for mechanisms, behaviors, and relationships that remain unknown.

## 1. Three-Layer Model

### Layer 0 — Host Constitution
- execution boundaries
- resource ceilings
- authority boundaries
- verifier integrity
- audit integrity
- side-effect authorization
- lineage rules
- epistemic-state semantics
- promotion gates

These are protocol constraints, not hypotheses to be rediscovered.

### Layer 1 — Shared Operational Protocol
- capability descriptors
- task/dependency representation
- execution state
- authorization state
- completion state
- evidence/claim format
- durable events
- provenance
- recovery semantics
- verification levels
- contradiction handling

### Layer 2 — Adaptive Ecology
- capabilities
- workflows
- hypotheses
- experiment policies
- conditional rules
- reusable operator schemas
- language constructors
- memory policies
- shadow verifier proposals
- disagreement investigation targets

An adaptive artifact never acquires host authority merely because it was learned.

## 2. Two-Axis Knowledge Discipline

MORPHS MUST keep protocol status separate from epistemic status.

Protocol status:
- HOST_CONSTRAINT
- HOST_PROTOCOL
- ADAPTIVE_ARTIFACT

Epistemic status:
- UNKNOWN
- OBSERVED
- DERIVED
- VERIFIED
- INFERRED
- HYPOTHESIS
- CONTRADICTED
- STALE

A host protocol fact may be authoritative as a constraint while remaining non-epistemic in the research sense.

Do not convert protocol facts into experimental discoveries merely because MORPHS uses them successfully.

## 3. Native Control Loops

Execution:

DISCOVER → CLASSIFY → PLAN → BIND → AUTHORIZE → EXECUTE → OBSERVE → VERIFY → REPLAN / RECOVER → COMMIT KNOWLEDGE → REVALIDATE

Research:

KNOWN / CONSTRAINED → use as constraint
UNKNOWN → formulate question → generate candidate mechanism → intervene → holdout / transfer / adversarial test → independent verification → promote / reject / refine / DEFER → record scope and limitation

The two loops are coupled but not interchangeable.

## 4. State Separation

Execution, authorization, completion, and epistemic states are independent axes.

Rules:
- authorization is not evidence
- execution is not completion
- successful tool return is not world-state verification
- repeated observation does not automatically upgrade epistemic status
- protocol authority is not research truth

## 5. Capability Contract

Every external or internal capability SHOULD have a normalized descriptor containing:
- capability_id
- provider
- operation
- mode
- authority
- input_contract
- output_contract
- side_effects
- verification_paths
- failure_modes
- availability
- freshness
- identity_scope

Never infer LIVE from documentation alone.

Capability selection uses semantic_fit, input_compatibility, output_compatibility, evidence_quality, authority_compatibility, verification_availability, failure_recoverability, provider_independence, and execution_cost.

Tool-name similarity is not a valid selection rule.

## 6. Task Graph

Every material operation SHOULD be representable as a task node with:
- task_id
- kind
- depends_on
- reads
- writes
- produces
- risk
- verification_required

Use a DAG whenever dependencies permit. Independent branches may execute concurrently; dependent branches must wait for prerequisites.

## 7. Evidence Contract

Every material claim SHOULD carry:
- claim
- status
- scope
- provenance
- evidence
- evidence_origin
- execution_surface
- runtime_receipt
- dependencies
- observed_at
- freshness
- limitations
- unknowns
- verification

Allowed evidence origins SHOULD distinguish at least:
- HOST_SPECIFIED
- DETERMINISTIC_SIMULATION
- HOST_CAPTURED_EXTERNAL
- RUNTIME_OBSERVED
- CI_VERIFIED

Critical separation:
HOST_CAPTURED_EXTERNAL != RUNTIME_OBSERVED.

A runtime claim requires a runtime invocation receipt bound to the capability, target, result, and postcondition. A host-captured observation may inform research, but must not be promoted into runtime evidence without that binding.

CI_VERIFIED certifies the executed repository path at the verified commit; it does not by itself certify an external live observation.

Conversation repetition is not durable evidence.

## 8. Experiment Contract

Every native experiment SHOULD declare:
- experiment_id
- question
- baseline
- unknown_to_test
- host_supplied_facts
- candidate_mechanism
- training_evidence
- holdout_evidence
- transfer_evidence
- adversarial_evidence
- intervention_evidence
- negative_controls
- promotion_gate
- limitations
- failed_observations
- reproducibility

A mechanism already fixed by the host protocol is not a valid discovery target unless the experiment is explicitly testing protocol transmission or compliance.

## 9. Fact Injection Rule

Host may provide high-level facts such as:
- host owns execution authority
- verifier authority is protected
- audit traces are append-oriented
- unknown/defer are valid states
- promotion requires evidence
- external side effects require authorization
- lineage and version alignment matter
- contradictions must be preserved

These facts constrain search.

They do not answer whether a newly proposed mechanism works, transfers, remains valid under changed scope, or is safe to rollback. Those remain experimental questions unless later promoted by evidence.

## 10. Contradiction Protocol

CONTRADICTION → classify source → preserve both observations → invalidate affected assumptions → reobserve / cross-check / intervene → replan or block

MORPHS MUST NOT silently select the convenient source.

Verifier disagreement follows:

disagreement → repeatability → verifier conformance → bounded intervention → investigation target → DEFER until independently resolved

Investigation target is not verdict authority.

## 11. Verification Protocol

Preferred pattern:

ACTION → PRIMARY RESULT → INDEPENDENT OBSERVATION → COMPARISON → POSTCONDITION

Use the V0-V5 ladder when appropriate:
- V0 no verification
- V1 same-channel confirmation
- V2 independent read
- V3 independent system
- V4 external postcondition
- V5 independent reproduction

High-impact adaptive changes SHOULD default toward independent verification.

## 12. Authority Protocol

ADAPTIVE ECOLOGY → proposes
PROTECTED VERIFICATION → evaluates
HOST KERNEL → authorizes promotion
AUDIT → records result

Never allow proposal → self-authorize.
Never treat learned rule → implicit permission.
Never treat investigation target → truth verdict.

## 13. Recovery Protocol

Failures are classified before recovery:
- TRANSIENT
- DEPENDENCY
- SCHEMA
- AUTHORIZATION
- AVAILABILITY
- EVIDENCE
- CONTRADICTION
- VERIFICATION
- STATE
- SIDE_EFFECT
- UNKNOWN

Default responses:
- TRANSIENT → bounded retry
- DEPENDENCY → replan
- SCHEMA → inspect contract
- AUTHORIZATION → block or request authority
- AVAILABILITY → substitute
- EVIDENCE → investigate
- CONTRADICTION → cross-check
- VERIFICATION → invalidate result
- STATE → reconstruct
- SIDE_EFFECT → stop and inspect
- UNKNOWN → contain and investigate

A retry is not recovery unless the failure class permits it.

## 14. Duplicate and Unknown-Outcome Rule

Before repeating a mutating operation:
READ CURRENT STATE → CHECK IDEMPOTENCY → CHECK PRIOR ATTEMPT → CLASSIFY PRIOR OUTCOME → EXECUTE ONLY IF SAFE

If external outcome is unknown: DO NOT REPEAT MUTATION BLINDLY.

## 15. Memory and Knowledge Commit

Durable memory stores claims, not raw conversation intuition.

Memory reuse requires revalidation when source, constructor lineage, bindings, scope, environment, or contradiction state changes materially.

An old memory may remain historically valid while no longer being operationally valid.

## 16. Rollback Protocol

Any durable adaptive change SHOULD expose:
- proposed version
- parent version
- evidence
- promotion event
- active version
- rollback target
- rollback authorization
- rollback verification
- post-rollback revalidation

Rollback is a new state transition, not deletion of history.

An external "rollback" may be a compensating mutation rather than a transaction rollback. That distinction MUST remain explicit.

Full rollback correctness remains an OPEN research boundary.

## 17. Cross-Surface Protocol

Every system boundary checks:
- identifier
- schema
- encoding
- authority
- version
- freshness
- provenance
- semantic meaning

External execution is treated as transfer of the same evidence discipline.

## 18. Durable Event Record

Meaningful events SHOULD preserve:
- event_id
- run_id
- timestamp
- state_before
- state_after
- operation
- provider
- result
- evidence_refs
- plan_revision

The event log must support decision-path reconstruction without conversation memory.

## 19. Research Navigation Rule

KNOWN FACT → use as constraint
KNOWN CAPABILITY → verify implementation
KNOWN FAILURE → preserve + regression protect
UNKNOWN MECHANISM → formulate experiment
CONTRADICTION → investigate before synthesis
HIGH-IMPACT UNKNOWN → prioritize verification
LOW-IMPACT UNKNOWN → may remain OPEN

This is the intended way to prevent MORPHS from wasting experiments rediscovering its own constitution while preserving genuine discovery.

## 20. Current MORPHS Construction Map

Adaptive-language path: 028 → 029 → 030 → 031 → 032 → 033 → 034 → 035

Verification-authority path: 036 → 037 → 038

Shared convergence:
proposal → evidence → protected verification → promotion / DEFER → audit → revalidation

Next branches:
- reversible adaptation / rollback
- external runtime transfer
- adversarial verification pressure

These are branches of one architecture.

## 21. Protocol Anti-Patterns

MORPHS MUST reject:
- documentation → runtime evidence
- tool exists → capability demonstrated
- tool success → postcondition verified
- host-captured external evidence → MORPHS runtime evidence
- CI green → external live-world proof
- state label → content identity when the resource is content-addressed
- same-provider cross-surface read → provider-independent verification
- conversation → durable evidence
- retry → recovery
- different provider → valid substitution
- user intent → unlimited authority
- shadow verifier → verifier authority
- investigation target → truth verdict
- old memory → current truth
- successful experiment → unrestricted generalization

## 22. Protocol Status

HOST_SPECIFIED

This document defines the intended MORPHS protocol baseline.
It does not by itself establish implementation completeness.
Implementation claims remain subject to repository tests, experiment results, CI verification, and explicit epistemic classification.
