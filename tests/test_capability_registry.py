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


@dataclass(frozen=True)
class BoundFixtureCapability:
    capability_id: str
    identity_scope: str

    def capability(self):
        return self


def test_registry_can_require_bound_invoker():
    registry = HostCapabilityRegistry()
    descriptor = BoundFixtureCapability("bound.read", "fixture/resource")
    registry.register(
        descriptor,
        lambda: "not-bound",
        AuthorizationState.ALLOW,
    )
    with pytest.raises(ValueError, match="invoker bound"):
        registry.register(
            BoundFixtureCapability("bound.write", "fixture/resource"),
            lambda: "not-bound",
            AuthorizationState.ALLOW,
            require_bound_invoker=True,
        )
    bound = BoundFixtureCapability("bound.ok", "fixture/resource")
    registry.register(
        bound,
        bound.capability,
        AuthorizationState.ALLOW,
        require_bound_invoker=True,
    )
