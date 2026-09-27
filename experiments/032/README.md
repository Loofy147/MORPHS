# Experiment 032 — Constructor-Language Evolution

## Question

Can MORPH modify its **active constructor vocabulary** by inducing a new reusable constructor from black-box traces, rather than merely selecting or rebinding an expression inside a fixed language?

This is harder than 031:

- 031 searched a generic AST grammar and induced reusable schemas.
- 032 promotes one such behavior into a **new named constructor in the active surface language**.
- The downstream rule must use the promoted constructor as an interface; the original constructor body is forbidden from the surface rule.

## Protocol

`black-box numeric traces → bounded constructor synthesis → train/holdout/transfer → promotion → interface rebinding → downstream composition → ablation → adversarial gate`

The mutation substrate exposes only generic constructors:

`ARG, CONST, ADD, SUB, LE, IF`

It does not expose a pre-named `abs`, `max`, `distance`, or other derived family.

The selected body was:

`if($a0<=$a1,($a1-$a0),($a0-$a1))`

The system promotes it as constructor `K0` only after it fits independent training episodes and unseen holdout/transfer traces.

## Verified result

- candidate constructor programs: 349,185
- promoted constructor: `K0`
- induced body: `if($a0<=$a1,($a1-$a0),($a0-$a1))`
- training fit: true
- holdout fit: true
- transfer fit: true
- interface rebinding: true
- downstream composite: 1.0
- downstream adversarial: 1.0
- no-constructor ablation: 0.7142857142857143
- decoy fits training: false
- semantic constructor name supplied: false

## CI verification

GitHub Actions run **39** completed successfully.

Verification:
- compile: success
- pytest: success
- Experiment 028: success
- Experiment 029: success
- Experiment 030: success
- Experiment 031: success
- Experiment 032: success

Run ID: `36330684366`
Job ID: `108651888355`
Commit: `7288fd1ca2df28812b11d9a61225b469fbf6982d`

## Why the ablation matters

After promotion, the downstream surface language uses `K0(a,b)`.

The original branch/subtraction body is explicitly forbidden from that surface rule. Removing the promoted constructor drops the same downstream task below perfect accuracy.

This is evidence that 032 is testing a change in the **active language interface**, not merely reporting another expression that could have been expanded inline.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic simulator with black-box numeric traces.

Important limitation: the mutation meta-language itself is supplied. 032 therefore tests evolution of the active constructor vocabulary, not unrestricted invention of arbitrary primitive evaluation semantics.

## Next pressure point

The remaining boundary is to let MORPH alter parts of the **constructor meta-language itself**, then prove that the altered substrate remains auditable, non-oracular, and useful under transfer.
