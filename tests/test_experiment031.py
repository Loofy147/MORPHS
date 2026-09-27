from morph_core.experiment031 import run_experiment031


def test_031_completes():
    assert run_experiment031()["experiment"] == "031_reusable_operator_schema_induction"


def test_generic_grammar_is_used():
    result = run_experiment031()
    assert result["grammar"]["predicate_count"] > 10000
    assert result["lineage"]["semantic_family_names_given"] is False


def test_reusable_schemas_generalize():
    result = run_experiment031()
    assert result["assertions"]["reusable_near_schema"]
    assert result["assertions"]["reusable_sum_schema"]


def test_composition_and_adversarial_gates():
    result = run_experiment031()
    assert result["assertions"]["composite_transfer"]
    assert result["assertions"]["adversarial_gate"]


def test_decoy_does_not_crossfit():
    assert run_experiment031()["assertions"]["decoy_does_not_crossfit"]


def test_expected_schemas_are_induced():
    result = run_experiment031()
    assert result["discovery"]["near_schema"] == "abs((s0-s1)) <= 1"
    assert result["discovery"]["sum_schema"] == "s2 == (s1+s0)"


def test_final_metrics_are_exact():
    result = run_experiment031()
    assert result["composition"]["final_accuracy"] == 1.0
    assert result["composition"]["adversarial_accuracy"] == 1.0


def test_deterministic():
    assert run_experiment031() == run_experiment031()
