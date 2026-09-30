from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class AuthorizationState(str, Enum):
    DENY = "DENY"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    ALLOW = "ALLOW"


@dataclass(frozen=True)
class RegisteredCapability:
    descriptor: Any
    authorization: AuthorizationState
    invoker: Callable[[], Any]


class HostCapabilityRegistry:
    """Minimal host-owned registry boundary for runtime capability binding.

    This is an experimental host fixture, not a claim that MORPHS already
    has a production capability registry.
    """

    def __init__(self) -> None:
        self._bindings: dict[str, RegisteredCapability] = {}

    def register(
        self,
        descriptor: Any,
        invoker: Callable[[], Any],
        authorization: AuthorizationState,
    ) -> None:
        capability_id = getattr(descriptor, "capability_id", "")
        if not capability_id:
            raise ValueError("capability descriptor requires capability_id")
        if capability_id in self._bindings:
            raise ValueError(f"capability already registered: {capability_id}")
        self._bindings[capability_id] = RegisteredCapability(
            descriptor=descriptor,
            authorization=authorization,
            invoker=invoker,
        )

    def resolve(self, capability_id: str) -> RegisteredCapability:
        try:
            return self._bindings[capability_id]
        except KeyError as exc:
            raise KeyError(f"unknown capability: {capability_id}") from exc

    def authorize(self, capability_id: str, expected_scope: str) -> RegisteredCapability:
        binding = self.resolve(capability_id)
        descriptor_scope = getattr(binding.descriptor, "identity_scope", "")
        if descriptor_scope != expected_scope:
            raise PermissionError("capability scope mismatch")
        if binding.authorization == AuthorizationState.DENY:
            raise PermissionError("capability is denied")
        if binding.authorization == AuthorizationState.APPROVAL_REQUIRED:
            raise PermissionError("capability requires approval")
        return binding

    def invoke(
        self,
        capability_id: str,
        expected_scope: str,
    ) -> Any:
        binding = self.authorize(capability_id, expected_scope)
        return binding.invoker()
