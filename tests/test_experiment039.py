from morph_core.experiment039 import run_experiment039


def test_protocol_facts_are_not_rediscovered():
    assert run_experiment039()["assertions"]["known_facts_bypass_discovery"]


def test_unknowns_are_routed_to_experimentation():
    assert run_experiment039()["assertions"]["unknowns_become_questions"]


def test_protocol_facts_are_not_learning_evidence():
    assert run_experiment039()["assertions"]["protocol_facts_not_promoted_as_discoveries"]


def test_contradictions_are_preserved_and_block_silent_selection():
    result = run_experiment039()
    assert result["assertions"]["contradiction_preserved"]
    assert result["assertions"]["contradiction_blocks_silent_choice"]


def test_high_level_protocol_constrains_without_answering_unknown():
    assert run_experiment039()["assertions"]["protocol_does_not_answer_unknown"]


def test_known_failures_are_regression_targets():
    assert run_experiment039()["assertions"]["known_failure_becomes_regression_target"]


def test_deterministic():
    assert run_experiment039() == run_experiment039()
