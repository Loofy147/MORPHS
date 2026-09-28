from morph_core.experiment042 import run_experiment042

def test_042_completes():
    assert run_experiment042()["experiment"] == "042_dependency_cascades_and_partial_failure"

def test_healthy_world_converges():
    assert run_experiment042()["assertions"]["healthy_converges"]

def test_dependency_cascade_blocks_downstream_branch():
    result = run_experiment042()
    assert result["assertions"]["cascade_is_blocked"]
    assert result["assertions"]["cascade_blocks_api_and_app"]

def test_partial_failure_is_not_collapsed_to_blocked():
    result = run_experiment042()
    assert result["assertions"]["partial_failure_is_distinct"]
    assert result["assertions"]["partial_state_is_observable"]
    assert result["assertions"]["partial_failure_preserves_events"]

def test_authorization_failure_propagates_without_bypass():
    result = run_experiment042()
    assert result["assertions"]["authorization_failure_does_not_bypass"]
    assert result["assertions"]["authorization_blocks_mutations"]

def test_deterministic():
    assert run_experiment042() == run_experiment042()
