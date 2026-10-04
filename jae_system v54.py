"""
===========================================================
JAE v54.0 — REAL-TIME SANDBOX WORLD STATE
              & CAUSAL SIMULATION ENGINE
===========================================================

安全原则：
REAL DATA
   ↓
VALIDATION
   ↓
FUSION
   ↓
SANDBOX WORLD STATE
   ↓
CAUSAL SIMULATION

数据层不能直接产生现实世界执行动作。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Iterable
import csv
import json
import math
import random
import statistics
from pathlib import Path


# =========================================================
# Utility
# =========================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


# =========================================================
# Audit
# =========================================================

class AuditLog:
    def __init__(self, path: Optional[str] = None):
        self.events: List[Dict[str, Any]] = []
        self.path = Path(path) if path else None

        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "timestamp": utc_now().isoformat(),
            "type": event_type,
            "payload": payload,
        }

        self.events.append(event)

        if self.path:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

        return event

    def export_csv(self, path: str = "jae_audit.csv") -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "type", "payload"])

            for event in self.events:
                writer.writerow([
                    event["timestamp"],
                    event["type"],
                    json.dumps(event["payload"], ensure_ascii=False),
                ])

    def export_jsonl(self, path: str = "jae_audit.jsonl") -> None:
        with open(path, "w", encoding="utf-8") as f:
            for event in self.events:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")


# =========================================================
# World State
# =========================================================

class WorldState:
    DEFAULT_VARIABLES = {
        "ai_capability": 0.50,
        "energy_stress": 0.30,
        "supply_chain_stress": 0.30,
        "financial_stress": 0.25,
        "geopolitical_risk": 0.30,
        "information_noise": 0.25,
        "climate_stress": 0.25,
        "economic_growth": 0.70,
    }

    def __init__(self, variables: Optional[Dict[str, float]] = None):
        self.variables = dict(self.DEFAULT_VARIABLES)

        if variables:
            for key, value in variables.items():
                self.variables[key] = clamp(value)

        self.history: List[Dict[str, Any]] = []

    def get(self, variable: str) -> Optional[float]:
        return self.variables.get(variable)

    def set(self, variable: str, value: float) -> None:
        self.variables[variable] = clamp(value)

    def ensure(self, variable: str, initial: float = 0.5) -> None:
        if variable not in self.variables:
            self.variables[variable] = clamp(initial)

    def snapshot(self) -> Dict[str, float]:
        return dict(self.variables)

    def restore(self, snapshot: Dict[str, float]) -> None:
        self.variables = dict(snapshot)

    def record_history(self) -> None:
        self.history.append({
            "timestamp": utc_now().isoformat(),
            "state": self.snapshot(),
        })


# =========================================================
# Source Profile
# =========================================================

@dataclass
class SourceProfile:
    source: str
    trust: float = 0.80
    freshness_half_life_s: float = 3600.0
    anomaly_threshold: float = 0.75
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.trust = clamp(self.trust)
        self.freshness_half_life_s = max(1.0, float(self.freshness_half_life_s))
        self.anomaly_threshold = clamp(self.anomaly_threshold)


# =========================================================
# Observation
# =========================================================

@dataclass
class Observation:
    variable: str
    value: float
    timestamp: str
    source: str
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def datetime(self) -> datetime:
        return parse_timestamp(self.timestamp)


# =========================================================
# Source Registry
# =========================================================

class SourceRegistry:
    def __init__(self):
        self.sources: Dict[str, SourceProfile] = {}

    def register(self, profile: SourceProfile) -> None:
        self.sources[profile.source] = profile

    def get(self, source: str) -> SourceProfile:
        if source not in self.sources:
            return SourceProfile(
                source=source,
                trust=0.50,
                freshness_half_life_s=1800.0,
            )

        return self.sources[source]


# =========================================================
# Freshness Model
# =========================================================

class FreshnessModel:
    """
    Exponential decay:
        freshness = exp(-ln(2) * age / half_life)
    """

    def calculate(
        self,
        observation: Observation,
        profile: SourceProfile,
        now: datetime,
    ) -> float:
        age = max(
            0.0,
            (now - observation.datetime()).total_seconds(),
        )

        half_life = profile.freshness_half_life_s

        return math.exp(
            -math.log(2) * age / half_life
        )


# =========================================================
# Anomaly Detection
# =========================================================

class AnomalyDetector:
    def score(self, value: float, peer_values: Iterable[float]) -> float:
        peers = list(peer_values)

        if len(peers) < 3:
            return 0.0

        median = statistics.median(peers)

        deviations = [
            abs(x - median)
            for x in peers
        ]

        mad = statistics.median(deviations)

        if mad < 1e-9:
            return 0.0

        robust_z = (
            0.6745
            * abs(value - median)
            / mad
        )

        return clamp(robust_z / 6.0)


# =========================================================
# Conflict Detection
# =========================================================

class ConflictDetector:
    def score(
        self,
        values: List[float],
        weights: List[float],
    ) -> float:
        if len(values) < 2:
            return 0.0

        total = sum(weights)

        if total <= 0:
            return 0.0

        mean = sum(
            value * weight
            for value, weight in zip(values, weights)
        ) / total

        variance = sum(
            weight * (value - mean) ** 2
            for value, weight in zip(values, weights)
        ) / total

        std = math.sqrt(max(0.0, variance))

        return clamp(std * 3.0)


# =========================================================
# Fusion Result
# =========================================================

@dataclass
class FusionResult:
    variable: str
    fused_value: float
    confidence: float
    observations_used: int
    observations_rejected: int
    conflict_score: float
    anomaly_score: float
    freshness_score: float
    source_scores: Dict[str, float]
    timestamp: str
    diagnostics: Dict[str, Any] = field(default_factory=dict)


# =========================================================
# Multi Source Fusion Engine
# =========================================================

class MultiSourceFusionEngine:
    def __init__(self, source_registry: SourceRegistry):
        self.sources = source_registry
        self.freshness = FreshnessModel()
        self.anomaly = AnomalyDetector()
        self.conflict = ConflictDetector()

    def fuse_variable(
        self,
        variable: str,
        observations: List[Observation],
        now: Optional[datetime] = None,
        min_confidence: float = 0.0,
        reject_anomaly: bool = True,
    ) -> FusionResult:
        now = now or utc_now()

        observations = [
            o for o in observations
            if o.variable == variable
        ]

        if not observations:
            return FusionResult(
                variable=variable,
                fused_value=float("nan"),
                confidence=0.0,
                observations_used=0,
                observations_rejected=0,
                conflict_score=0.0,
                anomaly_score=0.0,
                freshness_score=0.0,
                source_scores={},
                timestamp=now.isoformat(),
            )

        all_values = [o.value for o in observations]
        candidates = []
        rejected = 0
        max_anomaly = 0.0

        for observation in observations:
            profile = self.sources.get(observation.source)

            if not profile.enabled:
                rejected += 1
                continue

            if observation.confidence < min_confidence:
                rejected += 1
                continue

            peers = [
                o.value
                for o in observations
                if o is not observation
            ]

            anomaly_score = self.anomaly.score(
                observation.value,
                peers if len(peers) >= 3 else all_values,
            )

            max_anomaly = max(max_anomaly, anomaly_score)

            if (
                reject_anomaly
                and anomaly_score >= profile.anomaly_threshold
            ):
                rejected += 1
                continue

            freshness = self.freshness.calculate(
                observation,
                profile,
                now,
            )

            weight = (
                profile.trust
                * clamp(observation.confidence)
                * freshness
                * (1.0 - 0.5 * anomaly_score)
            )

            candidates.append(
                (
                    observation,
                    max(weight, 1e-9),
                    freshness,
                    profile.trust,
                )
            )

        if not candidates:
            return FusionResult(
                variable=variable,
                fused_value=float("nan"),
                confidence=0.0,
                observations_used=0,
                observations_rejected=rejected,
                conflict_score=1.0,
                anomaly_score=max_anomaly,
                freshness_score=0.0,
                source_scores={},
                timestamp=now.isoformat(),
            )

        values = [c[0].value for c in candidates]
        weights = [c[1] for c in candidates]
        total_weight = sum(weights)

        fused = sum(
            value * weight
            for value, weight in zip(values, weights)
        ) / total_weight

        conflict_score = self.conflict.score(values, weights)

        freshness_score = sum(
            freshness * weight
            for _, weight, freshness, _ in candidates
        ) / total_weight

        source_scores = {
            observation.source: trust
            for observation, _, _, trust in candidates
        }

        base_confidence = sum(
            observation.confidence * trust * weight
            for observation, weight, _, trust in candidates
        ) / total_weight

        final_confidence = clamp(
            base_confidence
            * freshness_score
            * (1.0 - 0.65 * conflict_score)
            * (1.0 - 0.25 * max_anomaly)
        )

        return FusionResult(
            variable=variable,
            fused_value=clamp(fused),
            confidence=final_confidence,
            observations_used=len(candidates),
            observations_rejected=rejected,
            conflict_score=conflict_score,
            anomaly_score=max_anomaly,
            freshness_score=freshness_score,
            source_scores=source_scores,
            timestamp=now.isoformat(),
            diagnostics={
                "weights": {
                    observation.source: weight
                    for observation, weight, _, _ in candidates
                }
            },
        )

    def fuse(
        self,
        observations: Iterable[Observation],
        variables: Optional[List[str]] = None,
        now: Optional[datetime] = None,
        min_confidence: float = 0.0,
        reject_anomaly: bool = True,
    ) -> Dict[str, FusionResult]:
        observations = list(observations)

        if variables is None:
            variables = sorted(
                set(o.variable for o in observations)
            )

        return {
            variable: self.fuse_variable(
                variable,
                observations,
                now=now,
                min_confidence=min_confidence,
                reject_anomaly=reject_anomaly,
            )
            for variable in variables
        }


# =========================================================
# Causal World Simulator
# =========================================================

@dataclass(frozen=True)
class CausalEdge:
    source: str
    target: str
    weight: float


class CausalWorldSimulator:
    DEFAULT_EDGES = [
        ("ai_capability", "economic_growth", 0.020),
        ("ai_capability", "information_noise", 0.010),
        ("energy_stress", "financial_stress", 0.030),
        ("energy_stress", "supply_chain_stress", 0.020),
        ("supply_chain_stress", "financial_stress", 0.020),
        ("geopolitical_risk", "energy_stress", 0.020),
        ("climate_stress", "supply_chain_stress", 0.020),
        ("financial_stress", "economic_growth", -0.030),
        ("information_noise", "geopolitical_risk", 0.010),
    ]

    def __init__(self, edges: Optional[List[CausalEdge]] = None):
        if edges is None:
            self.edges = [
                CausalEdge(*edge)
                for edge in self.DEFAULT_EDGES
            ]
        else:
            self.edges = list(edges)

    def add_edge(self, source: str, target: str, weight: float) -> None:
        self.edges.append(
            CausalEdge(source, target, weight)
        )

    def step(
        self,
        world: WorldState,
        dt: float = 1.0,
        shocks: Optional[Dict[str, float]] = None,
    ) -> Dict[str, float]:
        current = world.snapshot()
        deltas = {var: 0.0 for var in current}

        for edge in self.edges:
            if edge.source in current and edge.target in current:
                deltas[edge.target] += (
                    current[edge.source]
                    * edge.weight
                    * dt
                )

        if shocks:
            for var, delta in shocks.items():
                world.ensure(var)

                if var not in current:
                    value = world.get(var)
                    current[var] = 0.5 if value is None else value

                deltas.setdefault(var, 0.0)
                deltas[var] += float(delta)

        for var, delta in deltas.items():
            base = current.get(var)

            if base is None:
                base = world.get(var)

            if base is None:
                base = 0.5

            world.set(var, base + delta)

        world.record_history()
        return world.snapshot()


# =========================================================
# Realtime Sandbox Updater
# =========================================================

class RealtimeWorldStateUpdater:
    def __init__(
        self,
        world: WorldState,
        audit: AuditLog,
        fusion: MultiSourceFusionEngine,
    ):
        self.world = world
        self.audit = audit
        self.fusion = fusion
        self.snapshots: Dict[str, Dict[str, float]] = {}
        self.counter = 0

    def update(
        self,
        observations: Iterable[Observation],
        variables: Optional[List[str]] = None,
        min_confidence: float = 0.50,
        reject_anomaly: bool = True,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        now = now or utc_now()

        results = self.fusion.fuse(
            observations,
            variables=variables,
            now=now,
            min_confidence=min_confidence,
            reject_anomaly=reject_anomaly,
        )

        token = f"v54-{self.counter}"
        self.counter += 1

        self.snapshots[token] = self.world.snapshot()

        accepted = {}
        rejected = {}

        for variable, result in results.items():
            if math.isnan(result.fused_value):
                rejected[variable] = "no_valid_data"
                continue

            if variable not in self.world.variables:
                rejected[variable] = "unknown_variable"
                continue

            if result.confidence < min_confidence:
                rejected[variable] = "confidence_below_threshold"
                continue

            old = self.world.get(variable)

            self.world.set(variable, result.fused_value)

            accepted[variable] = {
                "old": old,
                "new": result.fused_value,
                "confidence": result.confidence,
                "conflict": result.conflict_score,
                "anomaly": result.anomaly_score,
                "freshness": result.freshness_score,
                "observations": result.observations_used,
            }

        self.world.record_history()

        self.audit.record(
            "v54_realtime_update",
            {
                "snapshot": token,
                "accepted": accepted,
                "rejected": rejected,
                "sandbox_only": True,
                "external_action": False,
            },
        )

        return {
            "snapshot": token,
            "accepted": accepted,
            "rejected": rejected,
            "results": results,
            "sandbox_only": True,
        }

    def rollback(self, token: str) -> Dict[str, Any]:
        if token not in self.snapshots:
            raise KeyError(token)

        before = self.world.snapshot()

        self.world.restore(self.snapshots[token])

        self.audit.record(
            "v54_rollback",
            {
                "snapshot": token,
                "sandbox_only": True,
                "external_action": False,
            },
        )

        return {
            "before": before,
            "after": self.world.snapshot(),
            "sandbox_only": True,
        }


# =========================================================
# JAE System
# =========================================================

class JAESystem:
    VERSION = "54.0.0"

    def __init__(
        self,
        seed: int = 54,
        audit_path: Optional[str] = None,
    ):
        random.seed(seed)

        self.audit = AuditLog(audit_path)
        self.world = WorldState()
        self.sources = SourceRegistry()

        self.fusion = MultiSourceFusionEngine(self.sources)

        self.updater = RealtimeWorldStateUpdater(
            self.world,
            self.audit,
            self.fusion,
        )

        self.causal = CausalWorldSimulator()

        self.audit.record(
            "system_start",
            {
                "version": self.VERSION,
                "sandbox": True,
                "external_action": False,
            },
        )

    def register_source(
        self,
        source: str,
        trust: float = 0.80,
        freshness_half_life_s: float = 3600.0,
        anomaly_threshold: float = 0.75,
    ) -> None:
        profile = SourceProfile(
            source=source,
            trust=trust,
            freshness_half_life_s=freshness_half_life_s,
            anomaly_threshold=anomaly_threshold,
        )

        self.sources.register(profile)

        self.audit.record(
            "source_registered",
            {
                "source": source,
                "trust": profile.trust,
            },
        )

    def ingest(
        self,
        observations: Iterable[Observation],
        variables: Optional[List[str]] = None,
        min_confidence: float = 0.50,
        reject_anomaly: bool = True,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        return self.updater.update(
            observations,
            variables=variables,
            min_confidence=min_confidence,
            reject_anomaly=reject_anomaly,
            now=now,
        )

    def simulate(
        self,
        steps: int = 1,
        dt: float = 1.0,
        shocks: Optional[Any] = None,
    ) -> Dict[int, Dict[str, float]]:
        results = {}

        for i in range(steps):
            shock = {}

            if shocks:
                if isinstance(shocks, dict):
                    shock = shocks.get(i, {})
                elif isinstance(shocks, list) and i < len(shocks):
                    shock = shocks[i]

            results[i] = self.causal.step(
                self.world,
                dt=dt,
                shocks=shock,
            )

        self.audit.record(
            "causal_simulation",
            {
                "steps": steps,
                "sandbox_only": True,
                "external_action": False,
            },
        )

        return results

    def rollback(self, token: str) -> Dict[str, Any]:
        return self.updater.rollback(token)

    def status(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "world": self.world.snapshot(),
            "sources": list(self.sources.sources.keys()),
            "audit_events": len(self.audit.events),
            "sandbox": True,
            "external_execution": False,
            "causal_edges": len(self.causal.edges),
        }

    def export_audit(
        self,
        csv_path: str = "jae_audit.csv",
        jsonl_path: Optional[str] = None,
    ) -> None:
        self.audit.export_csv(csv_path)

        if jsonl_path:
            self.audit.export_jsonl(jsonl_path)


# =========================================================
# Demo
# =========================================================

def demo():
    jae = JAESystem()

    jae.register_source(
        "macro_primary",
        trust=0.95,
        freshness_half_life_s=86400,
    )

    jae.register_source(
        "market_secondary",
        trust=0.78,
        freshness_half_life_s=3600,
    )

    now = utc_now()

    observations = [
        Observation(
            variable="energy_stress",
            value=0.44,
            timestamp=now.isoformat(),
            source="macro_primary",
            confidence=0.94,
        ),
        Observation(
            variable="energy_stress",
            value=0.48,
            timestamp=now.isoformat(),
            source="market_secondary",
            confidence=0.88,
        ),
        Observation(
            variable="ai_capability",
            value=0.76,
            timestamp=now.isoformat(),
            source="macro_primary",
            confidence=0.91,
        ),
        Observation(
            variable="geopolitical_risk",
            value=0.42,
            timestamp=now.isoformat(),
            source="macro_primary",
            confidence=0.90,
        ),
    ]

    result = jae.ingest(observations)

    print("\n========== JAE v54.0 ==========")
    print("Realtime World State")

    for variable, data in result["accepted"].items():
        print(
            f"{variable:25s}"
            f"value={data['new']:.4f} "
            f"confidence={data['confidence']:.4f} "
            f"freshness={data['freshness']:.4f}"
        )

    print("\nSnapshot:", result["snapshot"])
    print("Sandbox:", result["sandbox_only"])

    print("\nCausal simulation (3 steps):")
    sim = jae.simulate(steps=3)

    for step, state in sim.items():
        print(
            f"step {step}: "
            f"energy_stress={state['energy_stress']:.4f} "
            f"financial_stress={state['financial_stress']:.4f} "
            f"economic_growth={state['economic_growth']:.4f}"
        )

    print("\nWorld State:")
    for key, value in jae.world.variables.items():
        print(f"{key:25s} {value:.4f}")

    print("\nAudit events:", len(jae.audit.events))

    print("\nExecuting sandbox rollback...")
    rollback = jae.rollback(result["snapshot"])
    print("Rollback:", rollback["sandbox_only"])


if __name__ == "__main__":
    demo()