from morph_core.experiment038 import run_experiment038


def test_038_completes():
    assert run_experiment038()["experiment"] == "038_disagreement_investigation"


def test_claim_disagreement_is_localized():
    assert run_experiment038()["assertions"]["claim_disagreement_targets_claim"]


def test_verifier_fault_is_localized():
    assert run_experiment038()["assertions"]["verifier_fault_targets_verifier"]


def test_environment_instability_is_localized():
    assert run_experiment038()["assertions"]["instability_targets_environment"]


def test_unresolved_case_defers():
    assert run_experiment038()["assertions"]["unlocalized_case_remains_defer"]


def test_investigation_cannot_promote_truth():
    result = run_experiment038()
    assert result["assertions"]["investigation_does_not_grant_truth"]
    assert result["assertions"]["all_investigation_verdicts_remain_defer"]


def test_deterministic():
    assert run_experiment038() == run_experiment038()
