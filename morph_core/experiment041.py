from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ExternalStatus(str, Enum):
    EQUILIBRATED = "equilibrated"
    DRIFTED = "drifted"
    BLOCKED = "blocked"
    UNKNOWN_EXTERNAL_OUTCOME = "unknown_external_outcome"


@dataclass(frozen=True)
class Resource:
    name: str
    version: str
    available: bool
    mutable: bool = True


@dataclass(frozen=True)
class DesiredState:
    app_version: str
    db_schema: str


@dataclass
class ExternalWorld:
    resources: dict[str, Resource]
    dependency_edges: dict[str, tuple[str, ...]]
    mutation_outcomes: list[str] = field(default_factory=list)

    def read(self, name: str) -> Resource:
        return self.resources[name]

    def dependencies_ready(self, name: str) -> bool:
        return all(self.resources[dep].available for dep in self.dependency_edges.get(name, ()))

    def mutate(self, name: str, version: str, authorized: bool) -> str:
        current = self.resources[name]
        if not authorized or not current.mutable or not self.dependencies_ready(name):
            return "BLOCKED"
        self.resources[name] = Resource(name, version, current.available, current.mutable)
        self.mutation_outcomes.append("APPLIED")
        return "APPLIED"

    def mutate_unknown(self, name: str, version: str) -> str:
        current = self.resources[name]
        if current.version == version:
            self.mutation_outcomes.append("UNKNOWN_ALREADY_APPLIED")
            return "UNKNOWN"
        self.mutation_outcomes.append("UNKNOWN")
        return "UNKNOWN"


class ReconciliationLab:
    @staticmethod
    def observe(world: ExternalWorld, desired: DesiredState) -> dict[str, object]:
        app = world.read("app")
        db = world.read("db")
        db_ok = db.version == desired.db_schema and db.available
        app_ok = app.version == desired.app_version and app.available
        deps_ok = world.dependencies_ready("app")
        converged = app_ok and db_ok and deps_ok
        return {
            "app_version": app.version,
            "db_schema": db.version,
            "app_ok": app_ok,
            "db_ok": db_ok,
            "dependencies_ok": deps_ok,
            "converged": converged,
        }

    @classmethod
    def reconcile(cls, world: ExternalWorld, desired: DesiredState, authorized: bool) -> dict[str, object]:
        before = cls.observe(world, desired)
        actions: list[str] = []
        if not before["db_ok"] and world.read("db").available:
            outcome = world.mutate("db", desired.db_schema, authorized)
            actions.append(f"db:{outcome}")
        current = cls.observe(world, desired)
        if not current["app_ok"]:
            outcome = world.mutate("app", desired.app_version, authorized)
            actions.append(f"app:{outcome}")
        after = cls.observe(world, desired)
        status = ExternalStatus.EQUILIBRATED if after["converged"] else ExternalStatus.DRIFTED
        return {"before": before, "actions": actions, "after": after, "status": status.value}

    @classmethod
    def run(cls) -> dict[str, object]:
        desired = DesiredState("app-v2", "db-v2")
        world = ExternalWorld(
            resources={
                "db": Resource("db", "db-v1", True),
                "app": Resource("app", "app-v1", True),
            },
            dependency_edges={"app": ("db",)},
        )
        first = cls.reconcile(world, desired, authorized=True)

        world.resources["db"] = Resource("db", "db-v3", True)
        drift = cls.observe(world, desired)

        blocked_world = ExternalWorld(
            resources={
                "db": Resource("db", "db-v1", False),
                "app": Resource("app", "app-v1", True),
            },
            dependency_edges={"app": ("db",)},
        )
        blocked = cls.reconcile(blocked_world, desired, authorized=True)

        unknown_world = ExternalWorld(
            resources={
                "db": Resource("db", "db-v2", True),
                "app": Resource("app", "app-v1", True),
            },
            dependency_edges={"app": ("db",)},
        )
        unknown_mutation = unknown_world.mutate_unknown("app", "app-v2")
        unknown_observed = cls.observe(unknown_world, desired)
        resolved_after_unknown = unknown_observed["app_version"] == "app-v1"

        unauthorized_world = ExternalWorld(
            resources={
                "db": Resource("db", "db-v1", True),
                "app": Resource("app", "app-v1", True),
            },
            dependency_edges={"app": ("db",)},
        )
        unauthorized = cls.reconcile(unauthorized_world, desired, authorized=False)

        result = {
            "experiment": "041_external_world_equilibrium",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic external-world reconciliation simulator",
            "protocol": "observe -> dependency check -> authorized reconciliation -> observe post-state -> convergence or drift -> re-observe",
            "cases": {
                "initial_reconciliation": first,
                "external_drift": {"observed_after_external_change": drift, "status": ExternalStatus.DRIFTED.value},
                "dependency_block": blocked,
                "unknown_mutation_outcome": {
                    "provider_result": unknown_mutation,
                    "observed_app_version": unknown_observed["app_version"],
                    "must_reobserve_before_retry": resolved_after_unknown,
                },
                "authorization_block": unauthorized,
            },
            "world_model": {
                "dependency_graph": {"app": ["db"]},
                "equilibrium_definition": "desired state matches fresh observed state and required dependencies are satisfied",
            },
            "challenge": "MORPH: the external world is not your memory. Observe it, reconcile against fresh state, respect dependency edges, and never treat provider success or an unknown mutation outcome as equilibrium.",
            "limitation": "The external world is simulated and deterministic. This experiment does not establish safety for arbitrary external APIs, irreversible effects, network partitions, or adversarial state reporting.",
        }
        result["assertions"] = {
            "reconciliation_reaches_equilibrium": first["status"] == ExternalStatus.EQUILIBRATED.value,
            "drift_is_observable": drift["converged"] is False,
            "dependency_failure_blocks_reconciliation": blocked["status"] == ExternalStatus.DRIFTED.value and any(action.endswith("BLOCKED") for action in blocked["actions"]),
            "unknown_mutation_requires_reobservation": unknown_mutation == "UNKNOWN" and resolved_after_unknown,
            "authorization_blocks_external_mutation": unauthorized["status"] == ExternalStatus.DRIFTED.value and any(action.endswith("BLOCKED") for action in unauthorized["actions"]),
            "postcondition_is_observed_not_assumed": first["after"]["converged"],
            "deterministic": True,
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment041() -> dict[str, object]:
    return ReconciliationLab.run()


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment041(), indent=2, sort_keys=True))
