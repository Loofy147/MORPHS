# Experiment lineage

The MORPH research sequence currently contains 039 completed experiments in the local research lineage.

The sequence evolved through:
- capability composition and mutation
- attention and resource ecology
- tool discovery and workflow abstraction
- relation graphs and intervention testing
- adaptive experiment selection
- memory curation and conflicting hypotheses
- theory competition and blind generalization
- mechanical constitution induction
- induced machine-level rule language
- operator-language mutation
- reusable parameterized operator-schema induction
- active constructor-vocabulary evolution
- meta-language mutation under resource pressure
- budget-aware language evolution
- memory drift and constructor revalidation
- verifier shadow evolution
- independent verifier diversity
- disagreement investigation
- protocol grounding

Experiments 029-039 are the first native post-import experiments in the MORPHS repository.

## Verified burst

Experiments 033-035 are verified by GitHub Actions run 59.

Experiment 036 is verified by GitHub Actions run 68.

Experiment 037 is verified by GitHub Actions run 75.

Experiment 038 is verified by GitHub Actions run 88 (7 local tests also passed).

Experiment 039 is verified by GitHub Actions run 103.

The failed runs and fixture repairs preceding the verified burst are preserved as engineering evidence.

Repository policy:
1. Preserve original evidence.
2. Do not rewrite old experiments to match later interpretations.
3. Record supersession explicitly.
4. Keep epistemic status separate from implementation status.
5. Never upgrade a claim merely because it was repeated in later experiments.

## Current frontier

038 moves the verification path from simple disagreement handling toward controlled disagreement investigation:

disagreement → diagnose observable source → remain DEFER → independently resolve

The current protocol-grounding baseline is now repository-verified. The next frontier is to use it to reduce rediscovery while keeping unknown mechanisms genuinely experimental.

Likely pressure points:
- extend investigation coverage without turning probes into hidden truth rules
- rollback and irreversibility analysis for learned language changes
- external tool/runtime transfer
- adversarial attempts to influence verifier inputs or investigation traces

The full path map is maintained in docs/RESEARCH_PATHS.md.
