from morph_core.experiment036 import run_experiment036


def test_036_completes():
    assert run_experiment036()["experiment"] == "036_verifier_shadow_evolution"


def test_candidate_passes_independent_gates():
    result = run_experiment036()
    assert result["assertions"]["candidate_matches_training"]
    assert result["assertions"]["candidate_matches_holdout"]
    assert result["assertions"]["candidate_matches_anti_gaming"]


def test_decoys_cannot_game_promotion():
    assert run_experiment036()["assertions"]["decoys_rejected"]


def test_verifier_authority_remains_host_owned():
    result = run_experiment036()
    assert result["assertions"]["kernel_unchanged"]
    assert result["assertions"]["host_controls_promotion"]
    assert result["assertions"]["host_controls_kernel"]
    assert result["assertions"]["self_authority_denied"]


def test_expected_candidate():
    result = run_experiment036()
    assert result["search"]["promoted_candidate"] == (
        "train AND holdout AND transfer AND adversarial AND intervention "
        "AND lineage AND scope AND negative_control AND counterexamples == 0"
    )


def test_deterministic():
    assert run_experiment036() == run_experiment036()
