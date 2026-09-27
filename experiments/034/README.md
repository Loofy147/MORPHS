# Experiment 034 — Budget-Aware Language Evolution

## Question

Can MORPH decide when language evolution is worth its resource cost, rather than always mutating when mutation is available?

## Verified result

GitHub Actions run 59 passed the complete regression.

At budget 4.0:

- stable reuse → `reuse`
- blocked frontier → `evolve`
- expensive mutation → `reuse`
- uncertain mutation → `defer`

The policy uses hard feasibility gates for budget and mutation risk before comparing admissible alternatives.

## Repair history

The first scenario fixture accidentally allowed reuse in the high-risk uncertainty case, so the policy correctly chose reuse while the test incorrectly expected defer.

The fixture was corrected so the uncertainty case has no admissible reuse path while mutation remains above the risk limit. The resulting action is `defer`.

This was an experiment-fixture error, not evidence against the policy implementation.

## Epistemic status

**EXPERIMENTALLY_SUPPORTED**

Scope: deterministic symbolic decision simulator.

Limitation: values, costs, and risk are simulator inputs. The experiment supports policy behavior under explicit gates; it does not establish a universal utility law.
