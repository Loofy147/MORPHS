from dataclasses import dataclass

import pytest

from morph_core.capability_registry import (
    AuthorizationState,
    HostCapabilityRegistry,
)


@dataclass(frozen=True)
class FixtureCapability:
    capability_id: str
    identity_scope: str
    provider: str = "fixture"
    operation: str = "read"


def test_registry_resolves_and_invokes_allowed_capability():
    registry = HostCapabilityRegistry()
    descriptor = FixtureCapability("fixture.read", "fixture/resource")
    registry.register(
        descriptor,
        lambda: "invoked",
        AuthorizationState.ALLOW,
    )
    assert registry.invoke(
        "fixture.read",
        "fixture/resource",
    ) == "invoked"


def test_registry_rejects_denied_capability():
    registry = HostCapabilityRegistry()
    descriptor = FixtureCapability("fixture.read", "fixture/resource")
    registry.register(
        descriptor,
        lambda: "must-not-run",
        AuthorizationState.DENY,
    )
    with pytest.raises(PermissionError):
        registry.invoke("fixture.read", "fixture/resource")


def test_registry_rejects_approval_required_capability():
    registry = HostCapabilityRegistry()
    descriptor = FixtureCapability("fixture.read", "fixture/resource")
    registry.register(
        descriptor,
        lambda: "must-not-run",
        AuthorizationState.APPROVAL_REQUIRED,
    )
    with pytest.raises(PermissionError):
        registry.invoke("fixture.read", "fixture/resource")


def test_registry_rejects_scope_mismatch():
    registry = HostCapabilityRegistry()
    descriptor = FixtureCapability("fixture.read", "fixture/resource")
    registry.register(
        descriptor,
        lambda: "must-not-run",
        AuthorizationState.ALLOW,
    )
    with pytest.raises(PermissionError):
        registry.invoke("fixture.read", "other/resource")


def test_registry_rejects_duplicate_capability():
    registry = HostCapabilityRegistry()
    descriptor = FixtureCapability("fixture.read", "fixture/resource")
    registry.register(
        descriptor,
        lambda: "one",
        AuthorizationState.ALLOW,
    )
    with pytest.raises(ValueError):
        registry.register(
            descriptor,
            lambda: "two",
            AuthorizationState.ALLOW,
        )
