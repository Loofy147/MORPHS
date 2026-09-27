from morph_core.experiment037 import run_experiment037


def test_037_completes():
    assert run_experiment037()["experiment"] == "037_independent_verifier_diversity"


def test_clean_independent_verifiers_agree():
    result = run_experiment037()
    assert result["assertions"]["clean_agreement"]
    assert result["assertions"]["clean_candidate_promoted"]


def test_fault_injection_is_detected():
    result = run_experiment037()
    assert result["assertions"]["fault_injection_causes_disagreement"]
    assert result["assertions"]["disagreement_forces_defer"]


def test_candidate_cannot_override_disagreement():
    result = run_experiment037()
    assert result["assertions"]["candidate_cannot_override_disagreement"]


def test_independent_verifier_count():
    assert run_experiment037()["assertions"]["two_independent_verifiers"]


def test_deterministic():
    assert run_experiment037() == run_experiment037()
