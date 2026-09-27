from morph_core.experiment032 import run_experiment032


def test_032_completes():
    assert run_experiment032()["experiment"] == "032_constructor_language_evolution"


def test_searches_a_generic_mutation_substrate():
    result = run_experiment032()
    assert result["mutation_substrate"]["candidate_count"] > 300_000
    assert result["mutation_substrate"]["named_derived_families_given"] is False


def test_constructor_survives_holdout_and_transfer():
    result = run_experiment032()
    assert result["assertions"]["constructor_induced"]
    assert result["assertions"]["constructor_holdout"]
    assert result["assertions"]["constructor_transfer"]


def test_constructor_is_rebound_as_language_interface():
    assert run_experiment032()["assertions"]["interface_rebinding"]


def test_provenance_and_decoy_gates():
    result = run_experiment032()
    assert result["assertions"]["provenance_recorded"]
    assert result["assertions"]["decoy_rejected"]


def test_downstream_gates():
    result = run_experiment032()
    assert result["downstream"]["composite_accuracy"] == 1.0
    assert result["downstream"]["adversarial_accuracy"] == 1.0


def test_ablation_shows_surface_language_value():
    assert run_experiment032()["downstream"]["ablation_accuracy"] < 1.0


def test_expected_constructor_is_induced():
    result = run_experiment032()
    assert result["induction"]["body"] == (
        "if($a0<=$a1,($a1-$a0),($a0-$a1))"
    )


def test_deterministic():
    assert run_experiment032() == run_experiment032()
