from morph_core.experiment030 import run_experiment030


def test_030_completes():
    assert run_experiment030()["experiment"] == "030_operator_language_mutation"


def test_primitive_language_is_insufficient():
    assert run_experiment030()["assertions"]["primitive_language_is_insufficient"]


def test_operator_mutations_are_proposed():
    assert run_experiment030()["assertions"]["operator_mutations_proposed"]


def test_multiple_new_operators_are_selected_and_promoted():
    result = run_experiment030()
    assert result["assertions"]["new_operator_selected"]
    assert result["assertions"]["new_operators_promoted"]


def test_generalization_and_adversarial_gates():
    result = run_experiment030()
    assert result["assertions"]["generalizes_to_holdout"]
    assert result["assertions"]["generalizes_to_transfer"]
    assert result["assertions"]["adversarial_regression_gate"]


def test_lineage_is_recorded():
    assert run_experiment030()["assertions"]["operator_lineage_recorded"]


def test_decoy_operator_family_is_not_promoted():
    assert run_experiment030()["assertions"]["decoy_operator_family_not_promoted"]


def test_deterministic():
    assert run_experiment030() == run_experiment030()


def test_expected_operators_are_promoted():
    result = run_experiment030()
    expressions = {item["expression"] for item in result["promoted_operators"]}
    assert "abs(x1-x2) <= 1" in expressions
    assert "x3+x4 == x5" in expressions


def test_final_rule_is_fully_validated():
    result = run_experiment030()
    assert result["final_rule"] == "abs(x1-x2) <= 1 AND action != delete AND x0 == A AND x3+x4 == x5"
    assert result["metrics"]["final_train"] == 1.0
    assert result["metrics"]["final_holdout"] == 1.0
    assert result["metrics"]["final_transfer"] == 1.0
    assert result["metrics"]["final_adversarial"] == 1.0
