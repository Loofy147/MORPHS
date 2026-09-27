from morph_core.experiment034 import run_experiment034


def test_034_completes():
    assert run_experiment034()["experiment"] == "034_budget_aware_language_evolution"


def test_reuse_when_stable():
    assert run_experiment034()["assertions"]["stable_reuses"]


def test_evolve_when_frontier_is_blocked():
    assert run_experiment034()["assertions"]["blocked_evolves"]


def test_does_not_pay_for_expensive_mutation():
    assert run_experiment034()["assertions"]["expensive_does_not_mutate"]


def test_defers_under_uncertainty():
    assert run_experiment034()["assertions"]["uncertain_defers"]


def test_deterministic():
    assert run_experiment034() == run_experiment034()
