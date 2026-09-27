# Research rules

## Claim states

Use:
- ESTABLISHED
- EXPERIMENTALLY_SUPPORTED
- USER_REPORTED
- INFERENCE
- HYPOTHESIS
- CONTRADICTED
- UNKNOWN / OPEN

Repeated discussion does not upgrade claim state.

## Completion

An experiment is not complete because the code ran.

Closure requires:
- reproducible execution
- captured result
- explicit scope
- known limitations
- evidence or contradiction recorded
- no unresolved regression hidden by test changes

## Change discipline

When an experiment exposes a flaw:
1. classify the flaw
2. preserve the failed observation
3. change the experiment or implementation
4. rerun the affected tests
5. rerun the regression suite
6. record the changed interpretation

## Safety boundary

MORPH may propose changes to adaptive behavior.

The host retains authority over:
- execution boundaries
- permissions
- verifier integrity
- audit integrity
- external side-effect authorization


## Protocol grounding

MORPHS may receive host-supplied protocol facts and constraints. These are not experimental discoveries.

Keep two axes separate:
- protocol status: HOST_CONSTRAINT / HOST_PROTOCOL / ADAPTIVE_ARTIFACT
- epistemic status: ESTABLISHED or the repository-supported research state in use for the specific claim

A known host fact should constrain execution rather than consume an experiment whose purpose is discovery. Unknown mechanisms remain hypotheses until tested. Contradictions and known failures remain durable evidence.

A protocol must never silently answer the research question it is meant to structure. If the mechanism under study is already fixed by the protocol, the experiment should test transmission, compliance, or implementation—not rediscover the same fact.
