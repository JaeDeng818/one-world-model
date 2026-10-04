"""
===========================================================
JAE v53.0 — REAL-TIME WORLD STATE ENGINE
===========================================================

核心能力：
1. Multi-Source Data Fusion
2. Timestamp Alignment
3. Freshness Decay
4. Source Credibility
5. Conflict Detection
6. Robust Anomaly Detection
7. Real-Time Sandbox WorldState Update
8. Audit Log
9. Snapshot / Rollback
10. Causal World Simulation Interface

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
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Iterable, Optional, Any
import math
import statistics
import random
import csv
import json
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
        dt = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def clamp(value: float, low=0.0, high=1.0) -> float:
    return max(low, min(high, float(value)))


# =========================================================
# Audit
# =========================================================

class AuditLog:

    def __init__(self):
        self.events = []

    def record(self, event_type: str, payload: Dict[str, Any]):
        event = {
            "timestamp": utc_now().isoformat(),
            "type": event_type,
            "payload": payload,
        }

        self.events.append(event)

    def export_csv(self, path="jae_v53_audit.csv"):

        if not self.events:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:

            writer = csv.writer(f)

            writer.writerow([
                "timestamp",
                "type",
                "payload"
            ])

            for event in self.events:

                writer.writerow([
                    event["timestamp"],
                    event["type"],
                    json.dumps(
                        event["payload"],
                        ensure_ascii=False
                    )
                ])


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

    def __init__(self):

        self.variables = dict(
            self.DEFAULT_VARIABLES
        )

        self.history = []

    def get(self, variable):

        return self.variables.get(variable)

    def set(self, variable, value):

        self.variables[variable] = clamp(value)

    def snapshot(self):

        return dict(self.variables)

    def restore(self, snapshot):

        self.variables = dict(snapshot)

    def record_history(self):

        self.history.append({
            "timestamp": utc_now().isoformat(),
            "state": self.snapshot()
        })


# =========================================================
# Source Profile
# =========================================================

@dataclass
class SourceProfile:

    source: str

    trust: float = 0.80

    freshness_half_life_s: float = 3600

    anomaly_threshold: float = 0.75

    enabled: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self):

        self.trust = clamp(self.trust)

        self.freshness_half_life_s = max(
            1.0,
            self.freshness_half_life_s
        )


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

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def datetime(self):

        return parse_timestamp(
            self.timestamp
        )


# =========================================================
# Source Registry
# =========================================================

class SourceRegistry:

    def __init__(self):

        self.sources = {}

    def register(self, profile):

        self.sources[
            profile.source
        ] = profile

    def get(self, source):

        if source not in self.sources:

            # Unknown sources receive conservative defaults.
            return SourceProfile(
                source=source,
                trust=0.50,
                freshness_half_life_s=1800
            )

        return self.sources[source]


# =========================================================
# Freshness Model
# =========================================================

class FreshnessModel:

    """
    Exponential decay:

        freshness =
        exp(-ln(2) * age / half_life)
    """

    def calculate(
        self,
        observation,
        profile,
        now
    ):

        age = max(
            0,
            (
                now -
                observation.datetime()
            ).total_seconds()
        )

        half_life = (
            profile.freshness_half_life_s
        )

        return math.exp(
            -math.log(2)
            * age
            / half_life
        )


# =========================================================
# Anomaly Detection
# =========================================================

class AnomalyDetector:

    def score(
        self,
        value,
        peer_values
    ):

        if len(peer_values) < 3:

            return 0.0

        median = statistics.median(
            peer_values
        )

        deviations = [
            abs(x - median)
            for x in peer_values
        ]

        mad = statistics.median(
            deviations
        )

        if mad < 1e-9:

            return 0.0

        robust_z = (
            0.6745
            * abs(value - median)
            / mad
        )

        return clamp(
            robust_z / 6.0
        )


# =========================================================
# Conflict Detection
# =========================================================

class ConflictDetector:

    def score(
        self,
        values,
        weights
    ):

        if len(values) < 2:

            return 0.0

        total = sum(weights)

        if total <= 0:

            return 0.0

        mean = sum(
            value * weight
            for value, weight
            in zip(values, weights)
        ) / total

        variance = sum(
            weight
            * (value - mean) ** 2

            for value, weight
            in zip(values, weights)
        ) / total

        std = math.sqrt(
            max(0, variance)
        )

        return clamp(
            std * 3
        )


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

    diagnostics: Dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# Multi Source Fusion Engine
# =========================================================

class MultiSourceFusionEngine:

    def __init__(self, source_registry):

        self.sources = source_registry

        self.freshness = FreshnessModel()

        self.anomaly = AnomalyDetector()

        self.conflict = ConflictDetector()

    def fuse_variable(
        self,
        variable,
        observations,
        now=None,
        min_confidence=0.0,
        reject_anomaly=True
    ):

        now = now or utc_now()

        observations = [
            o for o in observations

            if o.variable == variable
        ]

        if not observations:

            return FusionResult(

                variable=variable,

                fused_value=float("nan"),

                confidence=0,

                observations_used=0,

                observations_rejected=0,

                conflict_score=0,

                anomaly_score=0,

                freshness_score=0,

                source_scores={},

                timestamp=now.isoformat()
            )

        peer_values = [
            o.value
            for o in observations
        ]

        candidates = []

        rejected = 0

        max_anomaly = 0

        for observation in observations:

            profile = self.sources.get(
                observation.source
            )

            if not profile.enabled:

                rejected += 1
                continue

            if (
                observation.confidence
                < min_confidence
            ):

                rejected += 1
                continue

            anomaly_score = (
                self.anomaly.score(
                    observation.value,
                    peer_values
                )
            )

            max_anomaly = max(
                max_anomaly,
                anomaly_score
            )

            if (
                reject_anomaly
                and
                anomaly_score
                >= profile.anomaly_threshold
            ):

                rejected += 1
                continue

            freshness = (
                self.freshness.calculate(
                    observation,
                    profile,
                    now
                )
            )

            weight = (

                profile.trust

                * clamp(
                    observation.confidence
                )

                * freshness

                * (
                    1
                    - 0.5
                    * anomaly_score
                )
            )

            candidates.append(
                (
                    observation,
                    max(weight, 1e-9),
                    freshness,
                    profile.trust
                )
            )

        if not candidates:

            return FusionResult(

                variable=variable,

                fused_value=float("nan"),

                confidence=0,

                observations_used=0,

                observations_rejected=rejected,

                conflict_score=1,

                anomaly_score=max_anomaly,

                freshness_score=0,

                source_scores={},

                timestamp=now.isoformat()
            )

        values = [
            x[0].value
            for x in candidates
        ]

        weights = [
            x[1]
            for x in candidates
        ]

        total_weight = sum(weights)

        fused = sum(
            value * weight
            for value, weight
            in zip(values, weights)
        ) / total_weight

        conflict_score = (
            self.conflict.score(
                values,
                weights
            )
        )

        freshness_score = sum(
            freshness * weight

            for (
                _,
                weight,
                freshness,
                _
            )
            in candidates
        ) / total_weight

        source_scores = {
            observation.source:
            trust

            for (
                observation,
                _,
                _,
                trust
            )
            in candidates
        }

        base_confidence = sum(

            observation.confidence
            * trust
            * weight

            for (
                observation,
                weight,
                _,
                trust
            )
            in candidates

        ) / total_weight

        final_confidence = clamp(

            base_confidence

            * freshness_score

            * (
                1
                - 0.65
                * conflict_score
            )

            * (
                1
                - 0.25
                * max_anomaly
            )
        )

        return FusionResult(

            variable=variable,

            fused_value=clamp(
                fused
            ),

            confidence=final_confidence,

            observations_used=len(
                candidates
            ),

            observations_rejected=rejected,

            conflict_score=conflict_score,

            anomaly_score=max_anomaly,

            freshness_score=freshness_score,

            source_scores=source_scores,

            timestamp=now.isoformat(),

            diagnostics={
                "weights": {
                    observation.source:
                    weight

                    for (
                        observation,
                        weight,
                        _,
                        _
                    )
                    in candidates
                }
            }
        )

    def fuse(
        self,
        observations,
        variables=None,
        now=None,
        min_confidence=0.0,
        reject_anomaly=True
    ):

        observations = list(
            observations
        )

        if variables is None:

            variables = sorted(
                set(
                    o.variable
                    for o in observations
                )
            )

        return {

            variable:
            self.fuse_variable(

                variable,

                observations,

                now=now,

                min_confidence=
                    min_confidence,

                reject_anomaly=
                    reject_anomaly
            )

            for variable
            in variables
        }


# =========================================================
# Real-Time Sandbox Updater
# =========================================================

class RealtimeWorldStateUpdater:

    def __init__(
        self,
        world,
        audit,
        fusion
    ):

        self.world = world

        self.audit = audit

        self.fusion = fusion

        self.snapshots = {}

        self.counter = 0

    def update(
        self,
        observations,
        variables=None,
        min_confidence=0.50,
        reject_anomaly=True,
        now=None
    ):

        now = now or utc_now()

        results = self.fusion.fuse(

            observations,

            variables=variables,

            now=now,

            min_confidence=
                min_confidence,

            reject_anomaly=
                reject_anomaly
        )

        token = (
            f"v53-{self.counter}"
        )

        self.counter += 1

        # Snapshot BEFORE mutation.
        self.snapshots[token] = (
            self.world.snapshot()
        )

        accepted = {}

        rejected = {}

        for variable, result in results.items():

            if math.isnan(
                result.fused_value
            ):

                rejected[
                    variable
                ] = "no_valid_data"

                continue

            if variable not in (
                self.world.variables
            ):

                rejected[
                    variable
                ] = "unknown_variable"

                continue

            if (
                result.confidence
                < min_confidence
            ):

                rejected[
                    variable
                ] = (
                    "confidence_below_threshold"
                )

                continue

            old = self.world.get(
                variable
            )

            self.world.set(
                variable,
                result.fused_value
            )

            accepted[
                variable
            ] = {

                "old": old,

                "new":
                    result.fused_value,

                "confidence":
                    result.confidence,

                "conflict":
                    result.conflict_score,

                "anomaly":
                    result.anomaly_score,

                "freshness":
                    result.freshness_score,

                "observations":
                    result.observations_used
            }

        self.world.record_history()

        self.audit.record(

            "v53_realtime_update",

            {

                "snapshot":
                    token,

                "accepted":
                    accepted,

                "rejected":
                    rejected,

                "sandbox_only":
                    True,

                "external_action":
                    False
            }
        )

        return {

            "snapshot":
                token,

            "accepted":
                accepted,

            "rejected":
                rejected,

            "results":
                results,

            "sandbox_only":
                True
        }

    def rollback(
        self,
        token
    ):

        if token not in (
            self.snapshots
        ):

            raise KeyError(
                token
            )

        before = (
            self.world.snapshot()
        )

        self.world.restore(
            self.snapshots[token]
        )

        self.audit.record(

            "v53_rollback",

            {

                "snapshot":
                    token,

                "sandbox_only":
                    True
            }
        )

        return {

            "before":
                before,

            "after":
                self.world.snapshot(),

            "sandbox_only":
                True
        }


# =========================================================
# JAE v53 System
# =========================================================

class JAEv53:

    VERSION = "53.0.0"

    def __init__(
        self,
        seed=53
    ):

        random.seed(seed)

        self.audit = AuditLog()

        self.world = WorldState()

        self.sources = (
            SourceRegistry()
        )

        self.fusion = (
            MultiSourceFusionEngine(
                self.sources
            )
        )

        self.updater = (
            RealtimeWorldStateUpdater(
                self.world,
                self.audit,
                self.fusion
            )
        )

        self.audit.record(

            "system_start",

            {

                "version":
                    self.VERSION,

                "sandbox":
                    True
            }
        )

    # -----------------------------------------------------
    # Source Management
    # -----------------------------------------------------

    def register_source(
        self,
        source,
        trust=0.80,
        freshness_half_life_s=3600,
        anomaly_threshold=0.75
    ):

        profile = SourceProfile(

            source=source,

            trust=trust,

            freshness_half_life_s=
                freshness_half_life_s,

            anomaly_threshold=
                anomaly_threshold
        )

        self.sources.register(
            profile
        )

        self.audit.record(

            "source_registered",

            {

                "source":
                    source,

                "trust":
                    trust
            }
        )

    # -----------------------------------------------------
    # Realtime Update
    # -----------------------------------------------------

    def ingest(
        self,
        observations,
        variables=None
    ):

        return self.updater.update(

            observations,

            variables=variables
        )

    # -----------------------------------------------------
    # Rollback
    # -----------------------------------------------------

    def rollback(
        self,
        token
    ):

        return self.updater.rollback(
            token
        )

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    def status(self):

        return {

            "version":
                self.VERSION,

            "world":
                self.world.snapshot(),

            "sources":
                list(
                    self.sources.sources.keys()
                ),

            "audit_events":
                len(
                    self.audit.events
                ),

            "sandbox":
                True,

            "external_execution":
                False
        }


# =========================================================
# Demo
# =========================================================

def demo():

    jae = JAEv53()

    # Source A
    jae.register_source(

        "macro_primary",

        trust=0.95,

        freshness_half_life_s=
            86400
    )

    # Source B
    jae.register_source(

        "market_secondary",

        trust=0.78,

        freshness_half_life_s=
            3600
    )

    now = utc_now()

    observations = [

        Observation(

            variable=
                "energy_stress",

            value=
                0.44,

            timestamp=
                now.isoformat(),

            source=
                "macro_primary",

            confidence=
                0.94
        ),

        Observation(

            variable=
                "energy_stress",

            value=
                0.48,

            timestamp=
                now.isoformat(),

            source=
                "market_secondary",

            confidence=
                0.88
        ),

        Observation(

            variable=
                "ai_capability",

            value=
                0.76,

            timestamp=
                now.isoformat(),

            source=
                "macro_primary",

            confidence=
                0.91
        ),

        Observation(

            variable=
                "geopolitical_risk",

            value=
                0.42,

            timestamp=
                now.isoformat(),

            source=
                "macro_primary",

            confidence=
                0.90
        )
    ]

    result = jae.ingest(
        observations
    )

    print(
        "\n========== JAE v53.0 =========="
    )

    print(
        "Realtime World State"
    )

    for variable, data in (
        result["accepted"].items()
    ):

        print(

            f"{variable:25s}"

            f"value={data['new']:.4f} "

            f"confidence="
            f"{data['confidence']:.4f} "

            f"freshness="
            f"{data['freshness']:.4f}"
        )

    print(
        "\nSnapshot:",
        result["snapshot"]
    )

    print(
        "Sandbox:",
        result["sandbox_only"]
    )

    print(
        "\nWorld State:"
    )

    for key, value in (
        jae.world.variables.items()
    ):

        print(
            f"{key:25s}"
            f"{value:.4f}"
        )

    print(
        "\nAudit events:",
        len(
            jae.audit.events
        )
    )

    # Test rollback
    print(
        "\nExecuting sandbox rollback..."
    )

    rollback = jae.rollback(
        result["snapshot"]
    )

    print(
        "Rollback:",
        rollback["sandbox_only"]
    )


# =========================================================
# Entry Point
# =========================================================

if __name__ == "__main__":

    demo()