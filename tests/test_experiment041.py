from morph_core.experiment041 import run_experiment041


def test_041_completes():
    assert run_experiment041()["experiment"] == "041_external_world_equilibrium"


def test_reconciliation_reaches_equilibrium():
    assert run_experiment041()["assertions"]["reconciliation_reaches_equilibrium"]


def test_external_drift_is_observable():
    assert run_experiment041()["assertions"]["drift_is_observable"]


def test_dependency_failure_blocks_reconciliation():
    assert run_experiment041()["assertions"]["dependency_failure_blocks_reconciliation"]


def test_unknown_mutation_requires_reobservation():
    assert run_experiment041()["assertions"]["unknown_mutation_requires_reobservation"]


def test_authorization_blocks_external_mutation():
    assert run_experiment041()["assertions"]["authorization_blocks_external_mutation"]


def test_postcondition_is_observed():
    assert run_experiment041()["assertions"]["postcondition_is_observed_not_assumed"]


def test_deterministic():
    assert run_experiment041() == run_experiment041()
