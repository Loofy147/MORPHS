# Experiment 038 — Disagreement Investigation

## Question

After 037 establishes **DEFER** on verifier disagreement, can MORPH investigate the source of disagreement without turning the investigation into a truth verdict?

## Protocol

`disagreement → repeatability → verifier audit → minimal intervention → investigation target → DEFER verdict`

The investigation has four possible target states:

- **CLAIM** — stable, conformant verifiers disagree only at an unspecified boundary.
- **VERIFIER** — at least one verifier violates a host-supplied audit contract.
- **ENVIRONMENT** — repeated identical input produces unstable verifier output.
- **DEFER** — the available probes do not localize the disagreement.

The investigator identifies a target of investigation. It never promotes a verdict from that target.

## Cases

### Claim-boundary disagreement

Two independently implemented, stable, conformant verifiers disagree only at boundary `0`, which is intentionally outside the supplied contract examples. The investigator targets **CLAIM**.

### Verifier fault

A fault-injected verifier omits the `negative_control` condition. The repeatability check is stable, but the protected audit contract fails. The investigator targets **VERIFIER**.

### Environment instability

A deliberately flaky verifier alternates output for identical input. The repeatability check fails, so the investigator targets **ENVIRONMENT**.

### Unresolved disagreement

Two stable, conformant verifiers disagree at boundary `2`, while the current minimal probe only checks `-1, 0, 1`. The disagreement is not localized, so the investigator remains at **DEFER**.

## Verification

- `python -m py_compile morph_core/experiment038.py tests/test_experiment038.py`
- `pytest -q tests/test_experiment038.py`
- result: **7 passed**

## CI verification

GitHub Actions run **88** completed successfully.

- compile: success
- pytest: success
- Experiments 028-037: success
- Experiment 038: success

Run ID: 36333611826
Job ID: 108660138696
Head commit: f737b3d1f3a8bb2eee4e5f423e69299cf59fff93

## Preserved engineering failure

The first local fixture for the unresolved case accidentally violated the verifier audit contract. That caused the investigator to classify the case as **VERIFIER** instead of reaching the intended unresolved path.

The fixture was corrected so both opaque verifiers satisfy the supplied audit contract while differing outside the probe range. The failed observation is preserved as a design/fixture failure, not erased.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: diagnostic simulator with host-supplied audit and probe mechanisms.

Limitation: the audit contract, intervention range, and ambiguity fixture are supplied by the host. The experiment supports the diagnostic policy only for these observable cases; it does not establish unrestricted automated root-cause identification.

## Research value

038 changes the rule from:

`disagreement → DEFER`

to:

`disagreement → investigate source → still DEFER until independently resolved`

The distinction matters: localization is evidence about where to investigate, not authority to decide the underlying claim.

## Next pressure points

- extend investigation coverage without turning probes into hidden truth rules
- test disagreement under rollback and irreversible state changes
- transfer the diagnostic protocol to external tools/runtime boundaries
- test adversarial attempts to corrupt verifier inputs or investigation traces
