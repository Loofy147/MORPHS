from morph_core.experiment029 import run_experiment029


def test_029_completes():
    result = run_experiment029()
    assert result["experiment"] == "029_induced_rule_language"


def test_machine_language_is_generated():
    assert run_experiment029()["assertions"]["language_generated_from_types"]


def test_candidate_synthesis_is_real():
    assert run_experiment029()["assertions"]["candidate_synthesis_occurred"]


def test_nontrivial_solution_exists():
    assert run_experiment029()["assertions"]["best_nontrivial_solution_exists"]


def test_holdout_and_transfer_generalize():
    result = run_experiment029()
    assert result["assertions"]["best_generalizes_to_holdout"]
    assert result["assertions"]["best_generalizes_to_transfer"]


def test_interventions_support_the_solution():
    assert run_experiment029()["assertions"]["intervention_evidence_present"]


def test_decoy_context_is_not_used():
    assert run_experiment029()["assertions"]["decoy_context_not_in_best"]


def test_action_constraint_is_discovered():
    assert run_experiment029()["assertions"]["action_delete_constraint_discovered"]


def test_no_human_semantic_rule_names():
    assert run_experiment029()["assertions"]["no_semantic_rule_names"]


def test_reproducible_result():
    assert run_experiment029() == run_experiment029()


def test_adversarial_challenge_passes():
    result = run_experiment029()
    assert result["assertions"]["adversarial_challenge_passed"]


def test_challenge_is_reported_in_metrics():
    result = run_experiment029()
    assert result["best_metrics"]["challenge"] == 1.0
