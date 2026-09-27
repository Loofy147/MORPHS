from morph_core.experiment035 import run_experiment035


def test_035_completes():
    assert run_experiment035()["experiment"] == "035_memory_drift_and_constructor_revalidation"


def test_known_memory_can_be_reused_across_rebinding():
    result = run_experiment035()
    assert result["assertions"]["stable_reuse"]
    assert result["assertions"]["rebound_reuse"]


def test_drift_demotes_old_memory():
    result = run_experiment035()
    assert result["assertions"]["drift_contradicts_old_memory"]
    assert result["assertions"]["old_memory_preserved"]


def test_replacement_requires_revalidation():
    result = run_experiment035()
    assert result["assertions"]["replacement_promoted_after_revalidation"]


def test_decoy_is_not_silently_trusted():
    result = run_experiment035()
    assert result["assertions"]["decoy_does_not_silently_validate_old_memory"]
    assert result["assertions"]["decoy_does_not_create_false_candidate"]


def test_deterministic():
    assert run_experiment035() == run_experiment035()
