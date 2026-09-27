from morph_core.experiment040 import run_experiment040

def test_040_completes():
    assert run_experiment040()["experiment"] == "040_reversible_adaptation"

def test_promotion_requires_verification_and_authority():
    result = run_experiment040()
    assert result["assertions"]["candidate_verified_before_promotion"]
    assert result["assertions"]["promotion_requires_authority"]

def test_valid_rollback_is_revalidated_and_history_is_preserved():
    result = run_experiment040()
    assert result["assertions"]["rollback_requires_revalidation"]
    assert result["assertions"]["rollback_preserves_history"]
    assert result["assertions"]["rollback_preserves_audit"]
    assert result["assertions"]["active_version_is_reverted"]

def test_unauthorized_transition_is_blocked():
    assert run_experiment040()["assertions"]["unauthorized_transition_blocked"]

def test_drift_blocks_stale_rollback():
    assert run_experiment040()["assertions"]["drift_blocks_stale_rollback"]

def test_audit_tamper_is_observable():
    assert run_experiment040()["assertions"]["audit_tamper_is_observable"]

def test_deterministic():
    assert run_experiment040() == run_experiment040()
