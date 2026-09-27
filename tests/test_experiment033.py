from morph_core.experiment033 import run_experiment033


def test_033_completes():
    assert run_experiment033()["experiment"] == "033_meta_language_binding_mutation"


def test_baseline_hits_resource_gate():
    result = run_experiment033()
    assert result["assertions"]["baseline_fails_resource_gate"]


def test_meta_language_mutation_reduces_cost():
    result = run_experiment033()
    assert result["assertions"]["mutation_found"]
    assert result["assertions"]["promotion_reduces_cost"]
    assert result["assertions"]["language_surface_changed"]


def test_generalizes_and_reuses():
    result = run_experiment033()
    assert result["assertions"]["holdout"]
    assert result["assertions"]["transfer"]
    assert result["assertions"]["downstream_reuse"]


def test_binding_is_not_optional():
    assert run_experiment033()["assertions"]["binding_is_required"]


def test_decoy_and_determinism():
    result = run_experiment033()
    assert result["assertions"]["decoy_control"]
    assert result["assertions"]["deterministic"]


def test_expected_mutation():
    result = run_experiment033()
    assert result["mutation"]["promoted"].startswith("let(")


def test_result_reproducible():
    assert run_experiment033() == run_experiment033()
