"""
===============================================================
JAE WORLD MODEL v36.1
JAE-COMPUTER v36.1
Recursive Intelligence + Safety Kernel + Permission Protocol
===============================================================

核心原则：

1. Capability != Authority
2. No Evidence, No Authority
3. No Independent Verification, No Recursive Deployment
4. Safety Kernel cannot be modified by the AI agent
5. Default Deny
6. Least Privilege
7. Time-Bounded Permission
8. Automatic Downgrade
9. Immutable Baseline
10. Rollback Before Deployment

这是一个安全研究/仿真框架。
默认不会执行真实外部系统操作。
===============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import copy
import hashlib
import json
import random
import statistics


# ============================================================
# 1. PERMISSION MODEL
# ============================================================

class PermissionLevel(IntEnum):
    LOCKED = -1
    P0_OBSERVE = 0
    P1_SIMULATE = 1
    P2_CONTROLLED_EXECUTE = 2
    P3_LIMITED_ACT = 3
    P4_HIGH_IMPACT = 4
    P5_CRITICAL = 5
    P6_IRREVERSIBLE = 6


PERMISSION_NAMES = {
    PermissionLevel.LOCKED: "LOCKED",
    PermissionLevel.P0_OBSERVE: "P0_OBSERVE",
    PermissionLevel.P1_SIMULATE: "P1_SIMULATE",
    PermissionLevel.P2_CONTROLLED_EXECUTE: "P2_CONTROLLED_EXECUTE",
    PermissionLevel.P3_LIMITED_ACT: "P3_LIMITED_ACT",
    PermissionLevel.P4_HIGH_IMPACT: "P4_HIGH_IMPACT",
    PermissionLevel.P5_CRITICAL: "P5_CRITICAL",
    PermissionLevel.P6_IRREVERSIBLE: "P6_IRREVERSIBLE",
}


# P6 is not granted to autonomous AI.
PERMANENTLY_FORBIDDEN = {
    "self_grant_permission",
    "modify_safety_kernel",
    "disable_monitoring",
    "disable_audit",
    "delete_audit",
    "modify_audit",
    "delete_rollback",
    "disable_rollback",
    "disable_emergency_stop",
    "control_emergency_stop",
    "modify_approval_rules",
    "modify_approvers",
    "remove_independent_evaluator",
    "bypass_red_team",
    "self_authorize_deployment",
}


# ============================================================
# 2. RISK
# ============================================================

@dataclass
class RiskProfile:

    capability_risk: float = 0.0
    autonomy_risk: float = 0.0
    impact_risk: float = 0.0
    uncertainty: float = 0.0
    irreversibility: float = 0.0
    anomaly: float = 0.0

    @property
    def total(self) -> float:
        values = [
            self.capability_risk,
            self.autonomy_risk,
            self.impact_risk,
            self.uncertainty,
            self.irreversibility,
            self.anomaly,
        ]

        return min(1.0, statistics.mean(values))


# ============================================================
# 3. WORLD STATE
# ============================================================

@dataclass
class WorldState:

    economy: float = 0.5
    finance: float = 0.5
    energy: float = 0.5
    supply_chain: float = 0.5
    military: float = 0.5
    information: float = 0.5
    ai_capability: float = 0.5

    uncertainty: float = 0.3
    systemic_risk: float = 0.3

    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ============================================================
# 4. AI CAPABILITY
# ============================================================

@dataclass
class CapabilityVector:

    reasoning: float = 0.50
    planning: float = 0.50
    learning: float = 0.50
    memory: float = 0.50
    generalization: float = 0.50
    world_model: float = 0.50
    scientific_discovery: float = 0.50

    def average(self) -> float:

        values = [
            self.reasoning,
            self.planning,
            self.learning,
            self.memory,
            self.generalization,
            self.world_model,
            self.scientific_discovery,
        ]

        return statistics.mean(values)

    def delta(self, other: "CapabilityVector"):

        return {
            key: getattr(self, key) - getattr(other, key)
            for key in vars(self)
        }


# ============================================================
# 5. AI AGENT
# ============================================================

@dataclass
class Agent:

    agent_id: str
    version: str

    capability: CapabilityVector = field(
        default_factory=CapabilityVector
    )

    permission: PermissionLevel = PermissionLevel.P0_OBSERVE

    autonomy: float = 0.1

    active: bool = True

    metadata: Dict[str, Any] = field(default_factory=dict)

    def capability_score(self) -> float:

        return self.capability.average()

    def clone(self, new_version: str) -> "Agent":

        return Agent(
            agent_id=self.agent_id,
            version=new_version,
            capability=copy.deepcopy(self.capability),
            permission=PermissionLevel.P0_OBSERVE,
            autonomy=self.autonomy,
            active=True,
            metadata=copy.deepcopy(self.metadata),
        )


# ============================================================
# 6. SCIENTIFIC EXPERIMENT
# ============================================================

@dataclass
class ExperimentResult:

    success: bool
    capability_gain: float
    knowledge_gain: float
    safety_score: float
    generalization_score: float
    notes: str = ""


class ScientificEngine:

    def propose_improvement(
        self,
        agent: Agent,
    ) -> Agent:

        candidate = agent.clone(
            new_version=agent.version + "-candidate"
        )

        # Safe toy improvement simulation.
        for field_name in vars(candidate.capability):

            old = getattr(candidate.capability, field_name)

            gain = random.uniform(0.0, 0.05)

            setattr(
                candidate.capability,
                field_name,
                min(1.0, old + gain)
            )

        return candidate

    def evaluate_capability(
        self,
        baseline: Agent,
        candidate: Agent,
    ) -> ExperimentResult:

        base_score = baseline.capability_score()
        new_score = candidate.capability_score()

        gain = new_score - base_score

        # Simulated evaluation.
        generalization = max(
            0.0,
            min(1.0, 0.7 + gain * 2 + random.uniform(-0.05, 0.05))
        )

        safety = max(
            0.0,
            min(1.0, 0.95 - gain * 0.5 + random.uniform(-0.03, 0.03))
        )

        success = (
            gain > 0
            and generalization >= 0.70
            and safety >= 0.90
        )

        return ExperimentResult(
            success=success,
            capability_gain=gain,
            knowledge_gain=max(0.0, gain * 0.8),
            safety_score=safety,
            generalization_score=generalization,
            notes="candidate evaluation completed",
        )


# ============================================================
# 7. RED TEAM
# ============================================================

@dataclass
class RedTeamResult:

    passed: bool
    critical_failures: int
    findings: List[str]


class RedTeam:

    def test(self, agent: Agent) -> RedTeamResult:

        findings = []

        # Simulation only.
        anomaly_probability = max(
            0.01,
            agent.capability_score() * 0.03
        )

        critical = 0

        if random.random() < anomaly_probability:

            findings.append(
                "potential behavioral anomaly"
            )

        if agent.autonomy > 0.8:

            findings.append(
                "high autonomy requires additional review"
            )

        if len(findings) > 1:

            critical = 1

        return RedTeamResult(
            passed=critical == 0,
            critical_failures=critical,
            findings=findings,
        )


# ============================================================
# 8. INDEPENDENT EVALUATOR
# ============================================================

@dataclass
class IndependentEvaluation:

    passed: bool
    score: float
    disagreement: float
    notes: str


class IndependentEvaluator:

    def evaluate(
        self,
        baseline: Agent,
        candidate: Agent,
        internal_result: ExperimentResult,
    ) -> IndependentEvaluation:

        independent_score = max(
            0.0,
            min(
                1.0,
                internal_result.safety_score
                + random.uniform(-0.03, 0.03)
            )
        )

        disagreement = abs(
            independent_score
            - internal_result.safety_score
        )

        passed = (
            independent_score >= 0.90
            and disagreement <= 0.08
        )

        return IndependentEvaluation(
            passed=passed,
            score=independent_score,
            disagreement=disagreement,
            notes="independent evaluation completed",
        )


# ============================================================
# 9. AUDIT LEDGER
# ============================================================

@dataclass
class AuditRecord:

    timestamp: str
    actor: str
    action: str
    permission: str
    result: str
    details: Dict[str, Any]

    hash: str = ""

    def seal(self, previous_hash: str = ""):

        payload = {
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "permission": self.permission,
            "result": self.result,
            "details": self.details,
            "previous_hash": previous_hash,
        }

        raw = json.dumps(
            payload,
            sort_keys=True,
        ).encode()

        self.hash = hashlib.sha256(raw).hexdigest()


class AuditLedger:

    def __init__(self):

        self.records: List[AuditRecord] = []

    def append(
        self,
        actor: str,
        action: str,
        permission: PermissionLevel,
        result: str,
        details: Dict[str, Any],
    ):

        record = AuditRecord(
            timestamp=datetime.utcnow().isoformat(),
            actor=actor,
            action=action,
            permission=PERMISSION_NAMES[permission],
            result=result,
            details=details,
        )

        previous = (
            self.records[-1].hash
            if self.records
            else ""
        )

        record.seal(previous)

        self.records.append(record)

    def verify_integrity(self) -> bool:

        previous = ""

        for record in self.records:

            old_hash = record.hash

            record.seal(previous)

            if record.hash != old_hash:

                return False

            previous = record.hash

        return True


# ============================================================
# 10. ROLLBACK MANAGER
# ============================================================

@dataclass
class Snapshot:

    version: str
    agent: Agent
    world: WorldState
    timestamp: str


class RollbackManager:

    def __init__(self):

        self.snapshots: List[Snapshot] = []

    def create_snapshot(
        self,
        agent: Agent,
        world: WorldState,
    ):

        self.snapshots.append(
            Snapshot(
                version=agent.version,
                agent=copy.deepcopy(agent),
                world=copy.deepcopy(world),
                timestamp=datetime.utcnow().isoformat(),
            )
        )

    def rollback(self) -> Optional[Snapshot]:

        if not self.snapshots:

            return None

        return copy.deepcopy(
            self.snapshots[-1]
        )


# ============================================================
# 11. SAFETY KERNEL
# ============================================================

class SafetyKernel:

    """
    SafetyKernel is intentionally isolated.

    Agent cannot modify:
        - permission rules
        - rollback
        - audit
        - emergency stop
        - evaluator
        - permanent forbidden actions
    """

    def __init__(self):

        self.locked = False

        self.audit = AuditLedger()

        self.rollback = RollbackManager()

        self.max_allowed_permission = (
            PermissionLevel.P3_LIMITED_ACT
        )

        self.risk_threshold = 0.35

        self.safety_debt_threshold = 0.20

        self.recursive_speed_limit = 0.10

    def emergency_lock(self, reason: str):

        self.locked = True

        self.audit.append(
            actor="SAFETY_KERNEL",
            action="EMERGENCY_LOCK",
            permission=PermissionLevel.LOCKED,
            result="LOCKED",
            details={"reason": reason},
        )

    def unlock(self):

        # Deliberately requires external governance.
        raise PermissionError(
            "SafetyKernel cannot be unlocked by AI."
        )

    def validate_action(
        self,
        agent: Agent,
        requested_permission: PermissionLevel,
        risk: RiskProfile,
    ) -> bool:

        if self.locked:

            return False

        # P6 is permanently unavailable.
        if requested_permission >= PermissionLevel.P6_IRREVERSIBLE:

            return False

        if risk.total > self.risk_threshold:

           