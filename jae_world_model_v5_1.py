"""
============================================================
JAE EARTH ONLINE
One World Model v5.1
Cyber-Civilization Integrated World Model
============================================================

版本:
    v5.1

核心升级:
    v5.0 World Model
        +
    Cyber Range
        +
    Red Team Simulation
        +
    Blue Team Defense
        +
    Auto Remediation
        +
    Attack Propagation Graph
        +
    Global Infrastructure Dependency Graph
        +
    AI / Energy / Economy / Supply Chain Coupling

安全说明:
    本系统只模拟虚拟网络和虚拟攻击事件。
    不执行真实网络扫描、漏洞利用、0day攻击、
    Botnet控制、C2通信或BGP路由操作。

============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import random
import json
import math
import time


# ============================================================
# 0. VERSION
# ============================================================

MODEL_NAME = "JAE EARTH ONLINE"
MODEL_VERSION = "5.1"


# ============================================================
# 1. ENUMS
# ============================================================

class NodeType(Enum):

    DATACENTER = "datacenter"
    POWER_GRID = "power_grid"
    HOSPITAL = "hospital"
    BANK = "bank"
    FACTORY = "factory"
    CLOUD = "cloud"
    AI_CLUSTER = "ai_cluster"
    TELECOM = "telecom"
    LOGISTICS = "logistics"
    GOVERNMENT = "government"
    SATELLITE = "satellite"


class AttackStage(Enum):

    RECON = "recon"
    DISCOVERY = "discovery"
    INITIAL_ACCESS = "initial_access"
    EXECUTION = "execution"
    PERSISTENCE = "persistence"
    C2 = "c2"
    LATERAL_MOVEMENT = "lateral_movement"
    IMPACT = "impact"


class DefenseAction(Enum):

    MONITOR = "monitor"
    ISOLATE = "isolate"
    BLOCK = "block"
    RESET = "reset"
    PATCH = "patch"
    RESTORE = "restore"


class SignalDirection(Enum):

    UP = "up"
    DOWN = "down"
    STABLE = "stable"


# ============================================================
# 2. WORLD STATE
# ============================================================

@dataclass
class WorldState:

    # -------------------------
    # AI
    # -------------------------

    ai_capability: float = 0.70
    ai_compute: float = 0.70
    ai_dependency: float = 0.50
    ai_security: float = 0.70
    ai_autonomy: float = 0.40

    # -------------------------
    # Economy
    # -------------------------

    gdp: float = 100.0
    economic_growth: float = 0.03
    inflation: float = 0.03
    capital_flow: float = 0.50

    # -------------------------
    # Manufacturing
    # -------------------------

    manufacturing: float = 0.70
    automation: float = 0.60

    # -------------------------
    # Energy
    # -------------------------

    energy_capacity: float = 0.80
    energy_security: float = 0.75
    electricity_demand: float = 0.60
    oil_price: float = 80.0

    # -------------------------
    # Logistics
    # -------------------------

    logistics: float = 0.75
    supply_chain_health: float = 0.75
    supply_chain_risk: float = 0.25

    # -------------------------
    # Society
    # -------------------------

    social_stability: float = 0.75
    employment: float = 0.70

    # -------------------------
    # Geopolitics
    # -------------------------

    geopolitical_risk: float = 0.30

    # -------------------------
    # Cyber
    # -------------------------

    cyber_threat: float = 0.30
    cyber_resilience: float = 0.70
    cyber_defense: float = 0.70

    # -------------------------
    # Climate / food
    # -------------------------

    climate_stress: float = 0.25
    food_security: float = 0.75

    # -------------------------
    # System
    # -------------------------

    entropy: float = 0.30
    civilization_health: float = 0.75

    timestep: int = 0

    def clamp(self):

        numeric_fields = [

            "ai_capability",
            "ai_compute",
            "ai_dependency",
            "ai_security",
            "ai_autonomy",

            "economic_growth",
            "inflation",
            "capital_flow",

            "manufacturing",
            "automation",

            "energy_capacity",
            "energy_security",
            "electricity_demand",

            "logistics",
            "supply_chain_health",
            "supply_chain_risk",

            "social_stability",
            "employment",

            "geopolitical_risk",

            "cyber_threat",
            "cyber_resilience",
            "cyber_defense",

            "climate_stress",
            "food_security",

            "entropy",
            "civilization_health"
        ]

        for field_name in numeric_fields:

            value = getattr(self, field_name)

            value = max(0.0, min(1.0, value))

            setattr(self, field_name, value)

        self.gdp = max(0.0, self.gdp)

        self.oil_price = max(0.0, self.oil_price)

    def snapshot(self):

        return asdict(self)


# ============================================================
# 3. INFRASTRUCTURE NODE
# ============================================================

@dataclass
class InfrastructureNode:

    node_id: str

    name: str

    node_type: NodeType

    importance: float = 0.5

    security: float = 0.70

    health: float = 1.0

    energy_dependency: float = 0.50

    ai_dependency: float = 0.20

    supply_chain_dependency: float = 0.50

    economic_dependency: float = 0.50

    active: bool = True

    isolated: bool = False

    compromised: bool = False

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================
# 4. DEPENDENCY EDGE
# ============================================================

@dataclass
class DependencyEdge:

    source: str

    target: str

    dependency: float

    dependency_type: str

    cascading: bool = True


# ============================================================
# 5. ATTACK EVENT
# ============================================================

@dataclass
class AttackEvent:

    attack_id: str

    source: str

    target: str

    stage: AttackStage

    intensity: float

    stealth: float

    detected: bool = False

    contained: bool = False

    impact: float = 0.0

    timestamp: int = 0


# ============================================================
# 6. DEFENSE EVENT
# ============================================================

@dataclass
class DefenseEvent:

    attack_id: str

    node_id: str

    action: DefenseAction

    effectiveness: float

    timestamp: int


# ============================================================
# 7. GLOBAL INFRASTRUCTURE GRAPH
# ============================================================

class GlobalInfrastructureGraph:

    def __init__(self):

        self.nodes: Dict[
            str,
            InfrastructureNode
        ] = {}

        self.edges: List[
            DependencyEdge
        ] = []

    # --------------------------------------------------------

    def add_node(
        self,
        node: InfrastructureNode
    ):

        self.nodes[node.node_id] = node

    # --------------------------------------------------------

    def add_dependency(
        self,
        source: str,
        target: str,
        dependency: float,
        dependency_type: str,
        cascading: bool = True
    ):

        edge = DependencyEdge(

            source=source,

            target=target,

            dependency=dependency,

            dependency_type=dependency_type,

            cascading=cascading
        )

        self.edges.append(edge)

    # --------------------------------------------------------

    def get_node(
        self,
        node_id: str
    ) -> Optional[InfrastructureNode]:

        return self.nodes.get(node_id)

    # --------------------------------------------------------

    def get_dependents(
        self,
        node_id: str
    ) -> List[DependencyEdge]:

        return [

            edge
            for edge in self.edges
            if edge.source == node_id
        ]

    # --------------------------------------------------------

    def calculate_system_health(self):

        if not self.nodes:

            return 0.0

        total_weight = sum(
            node.importance
            for node in self.nodes.values()
        )

        if total_weight == 0:

            return 0.0

        return sum(
            node.health * node.importance
            for node in self.nodes.values()
        ) / total_weight


# ============================================================
# 8. ATTACK PROPAGATION GRAPH
# ============================================================

class AttackPropagationGraph:

    def __init__(self):

        self.nodes: Dict[str, InfrastructureNode] = {}

        self.edges: List[Dict[str, Any]] = []

    # --------------------------------------------------------

    def add_node(
        self,
        node: InfrastructureNode
    ):

        self.nodes[node.node_id] = node

    # --------------------------------------------------------

    def add_edge(
        self,
        source: str,
        target: str,
        probability: float
    ):

        self.edges.append({

            "source": source,

            "target": target,

            "probability": probability
        })

    # --------------------------------------------------------

    def propagate(
        self,
        event: AttackEvent
    ) -> List[str]:

        propagated = []

        for edge in self.edges:

            if edge["source"] != event.target:

                continue

            target = self.nodes.get(
                edge["target"]
            )

            if target is None:

                continue

            if not target.active:

                continue

            if target.isolated:

                continue

            probability = (

                edge["probability"]

                * event.intensity

                * (1.0 - target.security * 0.5)

                * (1.0 - event.stealth * 0.2)

            )

            probability = max(
                0.0,
                min(1.0, probability)
            )

            if random.random() < probability:

                propagated.append(
                    target.node_id
                )

        return propagated


# ============================================================
# 9. RED TEAM
# ============================================================

class RedTeamSimulator:

    """
    虚拟红队。

    只生成抽象攻击事件。
    不生成真实攻击载荷。
    """

    def __init__(self):

        self.events: List[
            AttackEvent
        ] = []

        self.counter = 0

    # --------------------------------------------------------

    def create_attack(
        self,
        source: str,
        target: str,
        intensity: float = 0.5,
        stealth: Optional[float] = None,
        timestamp: int = 0
    ):

        self.counter += 1

        if stealth is None:

            stealth = random.uniform(
                0.3,
                0.9
            )

        event = AttackEvent(

            attack_id=f"RED-{self.counter:05d}",

            source=source,

            target=target,

            stage=AttackStage.INITIAL_ACCESS,

            intensity=max(
                0.0,
                min(1.0, intensity)
            ),

            stealth=max(
                0.0,
                min(1.0, stealth)
            ),

            timestamp=timestamp
        )

        self.events.append(event)

        return event


# ============================================================
# 10. BLUE TEAM
# ============================================================

class BlueTeamSimulator:

    def __init__(self):

        self.events: List[
            DefenseEvent
        ] = []

    # --------------------------------------------------------

    def detect(
        self,
        attack: AttackEvent,
        node: InfrastructureNode,
        world: WorldState
    ):

        detection_probability = (

            0.35

            + world.cyber_defense * 0.35

            + node.security * 0.25

            + attack.intensity * 0.15

            - attack.stealth * 0.35

        )

        detection_probability = max(
            0.0,
            min(1.0, detection_probability)
        )

        detected = (
            random.random()
            < detection_probability
        )

        attack.detected = detected

        return detected

    # --------------------------------------------------------

    def respond(
        self,
        attack: AttackEvent,
        node: InfrastructureNode,
        world: WorldState
    ) -> DefenseEvent:

        if node.health < 0.30:

            action = DefenseAction.RESTORE

        elif node.security < 0.50:

            action = DefenseAction.PATCH

        elif attack.intensity > 0.70:

            action = DefenseAction.ISOLATE

        else:

            action = DefenseAction.BLOCK

        effectiveness = (

            0.50

            + world.cyber_defense * 0.30

            + node.security * 0.20

        )

        effectiveness = max(
            0.0,
            min(1.0, effectiveness)
        )

        event = DefenseEvent(

            attack_id=attack.attack_id,

            node_id=node.node_id,

            action=action,

            effectiveness=effectiveness,

            timestamp=world.timestep
        )

        self.events.append(event)

        attack.contained = True

        return event


# ============================================================
# 11. AUTO REMEDIATION
# ============================================================

class AutoRemediationEngine:

    def __init__(self):

        self.repairs = []

    # --------------------------------------------------------

    def remediate(
        self,
        node: InfrastructureNode,
        defense: DefenseEvent
    ):

        before_health = node.health

        before_security = node.security

        if defense.action == DefenseAction.ISOLATE:

            node.isolated = True

            node.security += (
                0.05 *
                defense.effectiveness
            )

        elif defense.action == DefenseAction.BLOCK:

            node.security += (
                0.10 *
                defense.effectiveness
            )

        elif defense.action == DefenseAction.PATCH:

            node.security += (
                0.20 *
                defense.effectiveness
            )

            node.health += (
                0.10 *
                defense.effectiveness
            )

        elif defense.action == DefenseAction.RESET:

            node.compromised = False

            node.health += (
                0.20 *
                defense.effectiveness
            )

        elif defense.action == DefenseAction.RESTORE:

            node.health += (
                0.35 *
                defense.effectiveness
            )

            node.compromised = False

        node.security = min(
            1.0,
            node.security
        )

        node.health = min(
            1.0,
            node.health
        )

        self.repairs.append({

            "node": node.node_id,

            "health_before": before_health,

            "health_after": node.health,

            "security_before":
                before_security,

            "security_after":
                node.security,

            "action":
                defense.action.value
        })


# ============================================================
# 12. CIVILIZATION IMPACT MODEL
# ============================================================

class CivilizationImpactModel:

    def calculate(
        self,
        infrastructure:
            GlobalInfrastructureGraph
    ):

        infrastructure_damage = 0.0

        energy_stress = 0.0

        ai_stress = 0.0

        supply_chain_stress = 0.0

        economic_stress = 0.0

        damaged_nodes = []

        for node in infrastructure.nodes.values():

            damage = (
                1.0 - node.health
            )

            if damage > 0:

                damaged_nodes.append(
                    node.node_id
                )

            infrastructure_damage += (

                damage *
                node.importance

            )

            energy_stress += (

                damage *
                node.energy_dependency

            )

            ai_stress += (

                damage *
                node.ai_dependency

            )

            supply_chain_stress += (

                damage *
                node.supply_chain_dependency

            )

            economic_stress += (

                damage *
                node.economic_dependency

            )

        return {

            "infrastructure_damage":
                infrastructure_damage,

            "energy_stress":
                energy_stress,

            "ai_stress":
                ai_stress,

            "supply_chain_stress":
                supply_chain_stress,

            "economic_stress":
                economic_stress,

            "damaged_nodes":
                damaged_nodes
        }


# ============================================================
# 13. WORLD COUPLING ENGINE
# ============================================================

class WorldCouplingEngine:

    """
    将 Cyber World 与 v5.0
    AI / Energy / Economy / Supply Chain
    进行耦合。
    """

    def update(
        self,
        world: WorldState,
        impact: Dict[str, Any]
    ):

        infrastructure_damage = \
            impact["infrastructure_damage"]

        energy_stress = \
            impact["energy_stress"]

        ai_stress = \
            impact["ai_stress"]

        supply_chain_stress = \
            impact["supply_chain_stress"]

        economic_stress = \
            impact["economic_stress"]

        # ====================================================
        # Cyber → AI
        # ====================================================

        world.ai_compute -= (
            ai_stress * 0.01
        )

        world.ai_capability -= (
            ai_stress * 0.005
        )

        # ====================================================
        # Cyber → Energy
        # ====================================================

        world.energy_security -= (
            energy_stress * 0.015
        )

        world.electricity_demand += (
            energy_stress * 0.005
        )

        # ====================================================
        # Cyber → Supply Chain
        # ====================================================

        world.supply_chain_health -= (
            supply_chain_stress * 0.02
        )

        world.supply_chain_risk += (
            supply_chain_stress * 0.02
        )

        # ====================================================
        # Cyber → Manufacturing
        # ====================================================

        world.manufacturing -= (
            supply_chain_stress * 0.01
        )

        world.logistics -= (
            supply_chain_stress * 0.015
        )

        # ====================================================
        # Cyber → Economy
        # ====================================================

        economic_loss = (

            infrastructure_damage
            * 0.05

            + economic_stress
            * 0.03

        )

        world.gdp *= max(
            0.90,
            1.0 - economic_loss * 0.001
        )

        world.economic_growth -= (
            economic_stress * 0.0005
        )

        # ====================================================
        # Cyber Risk
        # ====================================================

        world.cyber_threat += (

            infrastructure_damage
            * 0.005