from datetime import datetime, timedelta, timezone

from morph_core.experiment043 import (
    CapabilityDescriptor,
    ExternalRuntimeTransfer,
    IndependentObservation,
    PrimaryObservation,
    VerificationState,
    run_experiment043,
)


def make_transfer(primary_content: str = "same", independent_content: str = "same", age_minutes: int = 0):
    observed = datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc)
    capability = CapabilityDescriptor(
        capability_id="fixture.read",
        provider="fixture",
        operation="read",
        mode="READ",
        authority="READ_ONLY",
        side_effects=(),
        verification_paths=("INDEPENDENT_READ",),
        failure_modes=("EVIDENCE", "STALE"),
        identity_scope="fixture/main",
    )
    primary = PrimaryObservation(
        provider="fixture",
        repository="fixture/repo",
        path="README.md",
        ref="main",
        commit_sha="commit-1",
        blob_sha="blob-1",
        content=primary_content,
        observed_at=observed,
    )
    independent = IndependentObservation(
        source="fixture.raw",
        repository="fixture/repo",
        path="README.md",
        ref="main",
        content=independent_content,
        observed_at=observed - timedelta(minutes=age_minutes),
    )
    return ExternalRuntimeTransfer(capability, lambda: primary, lambda: independent)


def test_043_clean_transfer_verifies():
    result = run_experiment043()
    assert result["assertions"]["clean_transfer_verified"]


def test_provider_success_is_not_postcondition():
    result = make_transfer("same", "different").execute(
        timedelta(minutes=5),
        datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc),
    )
    assert result.verification == VerificationState.DEFER.value
    assert "independent postcondition" in result.reason


def test_stale_observation_defers():
    result = make_transfer(age_minutes=10).execute(
        timedelta(minutes=5),
        datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc),
    )
    assert result.verification == VerificationState.DEFER.value
    assert result.reason == "stale observation"


def test_binding_mismatch_defers():
    transfer = make_transfer()
    original = transfer.independent_read
    transfer.independent_read = lambda: IndependentObservation(
        source="fixture.raw",
        repository="fixture/other",
        path="README.md",
        ref="main",
        content="same",
        observed_at=datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc),
    )
    result = transfer.execute(
        timedelta(minutes=5),
        datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc),
    )
    assert result.verification == VerificationState.DEFER.value
    assert result.reason == "cross-surface binding mismatch"
    assert original is not None


def test_capability_rejects_side_effects():
    base = CapabilityDescriptor(
        capability_id="fixture.write",
        provider="fixture",
        operation="write",
        mode="READ",
        authority="READ_ONLY",
        side_effects=("WRITE",),
        verification_paths=("INDEPENDENT_READ",),
        failure_modes=("SIDE_EFFECT",),
        identity_scope="fixture/main",
    )
    transfer = ExternalRuntimeTransfer(
        base,
        lambda: make_transfer().primary_read(),
        lambda: make_transfer().independent_read(),
    )
    try:
        transfer.execute(
            timedelta(minutes=5),
            datetime(2026, 9, 28, 8, 30, tzinfo=timezone.utc),
        )
    except ValueError as exc:
        assert "side effects" in str(exc)
    else:
        raise AssertionError("side-effecting capability was not rejected")


def test_deterministic():
    assert run_experiment043() == run_experiment043()


def test_runtime_integration_is_explicitly_open():
    result = run_experiment043()
    assert result["runtime_integration"]["status"] == "OPEN"
