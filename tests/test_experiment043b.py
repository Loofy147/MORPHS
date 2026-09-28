from morph_core.experiment043b import (
    MutationCapability,
    MutationDecision,
    MutationObservation,
    MutationPlan,
    ReversibleMutationProtocol,
    run_experiment043b,
)


def protocol():
    return ReversibleMutationProtocol(
        MutationCapability(
            capability_id="fixture.write",
            provider="fixture",
            operation="write",
            authority="WRITE",
            side_effects=("WRITE",),
            verification_paths=("INDEPENDENT_READ", "ROLLBACK_READ"),
        )
    )


def plan():
    return MutationPlan("baseline", "mutated", "baseline")


def test_043b_experiment_completes():
    assert run_experiment043b()["experiment"] == "043b_authorized_reversible_mutation"


def test_preflight_requires_expected_state():
    p = protocol()
    assert p.preflight(MutationObservation("baseline", "b"), plan(), True) == MutationDecision.APPLY
    assert p.preflight(MutationObservation("drifted", "d"), plan(), True) == MutationDecision.DEFER


def test_idempotency_prevents_duplicate_mutation():
    assert protocol().preflight(
        MutationObservation("mutated", "m"),
        plan(),
        True,
    ) == MutationDecision.NOOP_ALREADY_APPLIED


def test_unknown_outcome_is_not_blind_retry():
    result = protocol().classify_unknown(
        MutationObservation("partial", "p"),
        plan(),
    )
    assert result.decision == MutationDecision.DEFER.value
    assert result.safe_to_retry is False


def test_unknown_outcome_can_be_resolved_by_read():
    result = protocol().classify_unknown(
        MutationObservation("baseline", "b"),
        plan(),
    )
    assert result.outcome == "NOT_APPLIED"
    assert result.safe_to_retry is True


def test_postcondition_is_independent():
    result = protocol().verify_postcondition(
        MutationObservation("baseline", "b"),
        plan(),
    )
    assert result.decision == MutationDecision.DEFER.value
    assert result.rollback_allowed is False


def test_rollback_is_protected_against_drift():
    p = protocol()
    assert p.rollback_preflight(
        MutationObservation("mutated", "m"),
        plan(),
    ) == MutationDecision.APPLY
    assert p.rollback_preflight(
        MutationObservation("drifted", "d"),
        plan(),
    ) == MutationDecision.DEFER


def test_deterministic():
    assert run_experiment043b() == run_experiment043b()
