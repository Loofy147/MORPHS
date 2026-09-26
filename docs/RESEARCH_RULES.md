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
