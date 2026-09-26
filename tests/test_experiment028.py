from morph_core.experiment028 import run_experiment028


def test_four_core_invariants_are_induced():
    assert run_experiment028()["assertions"]["four_core_invariants_induced"]


def test_spurious_cost_rule_is_rejected():
    assert run_experiment028()["assertions"]["spurious_cost_rule_rejected"]


def test_spurious_context_rule_is_rejected():
    assert run_experiment028()["assertions"]["spurious_context_rule_rejected"]


def test_paired_interventions_are_used():
    assert run_experiment028()["assertions"]["paired_interventions_used"]


def test_transfer_context_is_used():
    assert run_experiment028()["assertions"]["transfer_context_used"]


def test_no_human_semantic_rules_are_learned():
    assert run_experiment028()["assertions"]["no_human_semantics"]


def test_evidence_is_required_for_every_candidate():
    assert run_experiment028()["assertions"]["evidence_required"]


def test_learning_is_reproducible():
    a = run_experiment028()
    b = run_experiment028()
    assert a["learned_invariants"] == b["learned_invariants"]
    assert a["hypotheses"] == b["hypotheses"]
