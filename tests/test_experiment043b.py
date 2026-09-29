from morph_core.experiment043b import (
    MutationAuthorization,
    MutationCapability,
    MutationDecision,
    MutationObservation,
    MutationPlan,
    ReversibleMutationProtocol,
    run_experiment043b,
)


def protocol():
    capability = MutationCapability(
        capability_id="fixture.write",
        provider="fixture",
        operation="write",
        authority="WRITE",
        side_effects=("WRITE",),
        verification_paths=("INDEPENDENT_READ", "ROLLBACK_READ"),
        identity_scope="fixture/scope",
    )
    authorization = MutationAuthorization(
        granted=True,
        authority_source="fixture-host",
        capability_id=capability.capability_id,
        scope=capability.identity_scope,
        allowed_side_effects=("WRITE",),
    )
    return ReversibleMutationProtocol(capability), authorization


def plan():
    return MutationPlan(
        "baseline",
        "baseline-blob",
        "mutated",
        "mutated-blob",
        "baseline",
        "baseline-blob",
    )


def test_043b_experiment_completes():
    result = run_experiment043b()
    assert result["experiment"] == "043b_authorized_reversible_mutation"
    assert result["runtime_integration"]["status"] == "OPEN"


def test_preflight_requires_exact_expected_identity():
    p, auth = protocol()
    assert p.preflight(MutationObservation("baseline", "baseline-blob"), plan(), auth) == MutationDecision.APPLY
    assert p.preflight(MutationObservation("baseline", "other-blob"), plan(), auth) == MutationDecision.DEFER
    assert p.preflight(MutationObservation("drifted", "drifted-blob"), plan(), auth) == MutationDecision.DEFER


def test_idempotency_requires_exact_desired_identity():
    p, auth = protocol()
    assert p.preflight(MutationObservation("mutated", "mutated-blob"), plan(), auth) == MutationDecision.NOOP_ALREADY_APPLIED
    assert p.preflight(MutationObservation("mutated", "other-blob"), plan(), auth) == MutationDecision.DEFER


def test_unknown_outcome_is_not_blind_retry():
    p, _ = protocol()
    result = p.classify_unknown(MutationObservation("partial", "p"), plan())
    assert result.decision == MutationDecision.DEFER.value
    assert result.safe_to_retry is False


def test_unknown_outcome_requires_exact_identity():
    p, _ = protocol()
    assert p.classify_unknown(MutationObservation("baseline", "baseline-blob"), plan()).outcome == "NOT_APPLIED"
    assert p.classify_unknown(MutationObservation("mutated", "mutated-blob"), plan()).outcome == "APPLIED"
    assert p.classify_unknown(MutationObservation("mutated", "other-blob"), plan()).decision == MutationDecision.DEFER.value


def test_postcondition_requires_exact_identity():
    p, _ = protocol()
    ok = p.verify_postcondition(MutationObservation("mutated", "mutated-blob"), plan())
    bad = p.verify_postcondition(MutationObservation("mutated", "other-blob"), plan())
    assert ok.rollback_allowed
    assert bad.decision == MutationDecision.DEFER.value
    assert bad.rollback_allowed is False


def test_rollback_is_protected_against_state_or_identity_drift():
    p, _ = protocol()
    assert p.rollback_preflight(MutationObservation("mutated", "mutated-blob"), plan()) == MutationDecision.APPLY
    assert p.rollback_preflight(MutationObservation("drifted", "mutated-blob"), plan()) == MutationDecision.DEFER
    assert p.rollback_preflight(MutationObservation("mutated", "newer-blob"), plan()) == MutationDecision.DEFER


def test_rollback_postcondition_requires_exact_target_identity():
    p, _ = protocol()
    ok = p.verify_rollback(MutationObservation("baseline", "baseline-blob"), plan())
    bad = p.verify_rollback(MutationObservation("baseline", "other-blob"), plan())
    assert ok.outcome == "APPLIED"
    assert bad.decision == MutationDecision.DEFER.value


def test_authorization_is_bound_to_capability_and_scope():
    p, auth = protocol()
    wrong = MutationAuthorization(
        granted=True,
        authority_source="wrong",
        capability_id="other.capability",
        scope="other/scope",
        allowed_side_effects=("WRITE",),
    )
    try:
        p.preflight(MutationObservation("baseline", "baseline-blob"), plan(), wrong)
    except PermissionError:
        pass
    else:
        raise AssertionError("unbound authorization was accepted")


def test_deterministic():
    assert run_experiment043b() == run_experiment043b()
