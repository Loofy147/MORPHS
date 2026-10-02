from __future__ import annotations

import os

from morph_core.capability_registry import (
    AuthorizationState,
    HostCapabilityRegistry,
)
from morph_core.experiment043c import GitHubRuntimeAdapter, JsonReceiptStore, run_experiment043c


def build_host_registry(adapter: GitHubRuntimeAdapter) -> HostCapabilityRegistry:
    authorization = os.environ.get("MORPHS_043C_AUTHORIZATION", "")
    if authorization != AuthorizationState.ALLOW.value:
        raise PermissionError(
            "043c host runner requires explicit MORPHS_043C_AUTHORIZATION=ALLOW"
        )

    registry = HostCapabilityRegistry()
    registry.register(
        adapter.capability(),
        adapter.invoke,
        AuthorizationState.ALLOW,
        require_bound_invoker=True,
    )
    return registry


def main() -> None:
    adapter = GitHubRuntimeAdapter(
        repository="Loofy147/MORPHS",
        path="README.md",
        ref="main",
    )
    registry = build_host_registry(adapter)
    receipt_store = JsonReceiptStore(
        os.environ.get(
            "MORPHS_043C_RECEIPT_PATH",
            "experiments/043c/runtime_receipt.json",
        )
    )
    print(
        run_experiment043c(
            registry=registry,
            receipt_store=receipt_store,
        )
    )


if __name__ == "__main__":
    main()
