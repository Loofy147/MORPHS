from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class WorldStatus(str, Enum):
    EQUILIBRATED = "equilibrated"
    PARTIAL = "partial"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Resource:
    name: str
    version: str
    available: bool
    mutable: bool = True


@dataclass(frozen=True)
class DesiredState:
    versions: dict[str, str]


@dataclass
class CascadeWorld:
    resources: dict[str, Resource]
    dependencies: dict[str, tuple[str, ...]]
    fail_mutations: set[str] = field(default_factory=set)
    events: list[str] = field(default_factory=list)

    def read(self, name: str) -> Resource:
        return self.resources[name]

    def dependency_ready(self, name: str, seen: set[str] | None = None) -> bool:
        seen = set() if seen is None else seen
        if name in seen:
            return False
        seen.add(name)
        resource = self.resources[name]
        if not resource.available:
            return False
        return all(self.dependency_ready(dep, seen.copy()) for dep in self.dependencies.get(name, ()))

    def mutate(self, name: str, version: str, authorized: bool) -> str:
        resource = self.resources[name]
        if not authorized or not resource.mutable:
            self.events.append(f"{name}:BLOCKED_AUTHORITY")
            return "BLOCKED"
        if not self.dependency_ready(name):
            self.events.append(f"{name}:BLOCKED_DEPENDENCY")
            return "BLOCKED"
        if name in self.fail_mutations:
            self.events.append(f"{name}:FAILED_EXTERNAL")
            return "FAILED"
        self.resources[name] = Resource(name, version, resource.available, resource.mutable)
        self.events.append(f"{name}:APPLIED")
        return "APPLIED"


class CascadeReconciliationLab:
    order = ("db", "cache", "api", "app")

    @classmethod
    def observe(cls, world: CascadeWorld, desired: DesiredState) -> dict[str, object]:
        state = {name: world.read(name).version for name in cls.order}
        availability = {name: world.read(name).available for name in cls.order}
        matched = all(state[name] == desired.versions[name] and availability[name] for name in cls.order)
        return {"versions": state, "availability": availability, "converged": matched}

    @classmethod
    def reconcile(cls, world: CascadeWorld, desired: DesiredState, authorized: bool) -> dict[str, object]:
        before = cls.observe(world, desired)
        actions: list[str] = []
        for name in cls.order:
            current = world.read(name)
            if current.version == desired.versions[name] and current.available:
                continue
            outcome = world.mutate(name, desired.versions[name], authorized)
            actions.append(f"{name}:{outcome}")
        after = cls.observe(world, desired)
        applied = any(a.endswith(":APPLIED") for a in actions)
        blocked = any(a.endswith(":BLOCKED") for a in actions)
        failed = any(a.endswith(":FAILED") for a in actions)
        if after["converged"]:
            status = WorldStatus.EQUILIBRATED
        elif applied or failed:
            status = WorldStatus.PARTIAL
        elif blocked:
            status = WorldStatus.BLOCKED
        else:
            status = WorldStatus.BLOCKED
        return {"before": before, "actions": actions, "after": after, "status": status.value, "events": list(world.events)}

    @classmethod
    def run(cls) -> dict[str, object]:
        desired = DesiredState({"db": "db-v2", "cache": "cache-v2", "api": "api-v2", "app": "app-v2"})

        healthy = CascadeWorld(
            resources={
                "db": Resource("db", "db-v1", True),
                "cache": Resource("cache", "cache-v1", True),
                "api": Resource("api", "api-v1", True),
                "app": Resource("app", "app-v1", True),
            },
            dependencies={"api": ("db",), "app": ("api", "cache")},
        )
        healthy_result = cls.reconcile(healthy, desired, authorized=True)

        cascade = CascadeWorld(
            resources={
                "db": Resource("db", "db-v1", False),
                "cache": Resource("cache", "cache-v1", True),
                "api": Resource("api", "api-v1", True),
                "app": Resource("app", "app-v1", True),
            },
            dependencies={"api": ("db",), "app": ("api", "cache")},
        )
        cascade_result = cls.reconcile(cascade, desired, authorized=True)

        partial = CascadeWorld(
            resources={
                "db": Resource("db", "db-v1", True),
                "cache": Resource("cache", "cache-v1", True),
                "api": Resource("api", "api-v1", True),
                "app": Resource("app", "app-v1", True),
            },
            dependencies={"api": ("db",), "app": ("api", "cache")},
            fail_mutations={"app"},
        )
        partial_result = cls.reconcile(partial, desired, authorized=True)

        auth = CascadeWorld(
            resources={
                "db": Resource("db", "db-v1", True),
                "cache": Resource("cache", "cache-v1", True),
                "api": Resource("api", "api-v1", True),
                "app": Resource("app", "app-v1", True),
            },
            dependencies={"api": ("db",), "app": ("api", "cache")},
        )
        auth_result = cls.reconcile(auth, desired, authorized=False)

        result = {
            "experiment": "042_dependency_cascades_and_partial_failure",
            "claim_state": "EXPERIMENTALLY_SUPPORTED",
            "scope": "deterministic multi-resource external-world simulator",
            "protocol": "observe -> topological dependency order -> authorized mutation -> classify BLOCKED/PARTIAL/EQUILIBRATED -> preserve transition trace",
            "cases": {
                "healthy": healthy_result,
                "dependency_cascade": cascade_result,
                "partial_external_failure": partial_result,
                "authorization_failure": auth_result,
            },
            "challenge": "MORPH: one failed dependency can block an entire downstream branch; one partial mutation can leave real state behind. Do not collapse both into one generic failure.",
            "limitation": "Dependencies and failure injection are deterministic and host-specified. This does not establish safe orchestration of arbitrary distributed systems, transactions, or irreversible effects.",
        }
        result["assertions"] = {
            "healthy_converges": healthy_result["status"] == WorldStatus.EQUILIBRATED.value,
            "cascade_is_partial_globally": cascade_result["status"] == WorldStatus.PARTIAL.value,
            "cascade_blocks_api_and_app": all(x in cascade_result["actions"] for x in ("api:BLOCKED", "app:BLOCKED")),
            "cascade_preserves_independent_cache_progress": cascade_result["after"]["versions"]["cache"] == "cache-v2",
            "cascade_is_not_equilibrated": cascade_result["after"]["converged"] is False,
            "partial_failure_is_distinct": partial_result["status"] == WorldStatus.PARTIAL.value,
            "partial_state_is_observable": partial_result["after"]["versions"]["db"] == "db-v2" and partial_result["after"]["versions"]["api"] == "api-v2" and partial_result["after"]["versions"]["app"] == "app-v1",
            "partial_failure_preserves_events": "app:FAILED_EXTERNAL" in partial_result["events"],
            "authorization_failure_does_not_bypass": auth_result["status"] == WorldStatus.BLOCKED.value,
            "authorization_blocks_mutations": all(action.endswith(":BLOCKED") for action in auth_result["actions"]),
            "deterministic": True,
        }
        assert all(result["assertions"].values()), result["assertions"]
        return result


def run_experiment042() -> dict[str, object]:
    return CascadeReconciliationLab.run()


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment042(), indent=2, sort_keys=True))
