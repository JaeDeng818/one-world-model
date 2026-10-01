"""
============================================================
JAE EARTH ONLINE
One World Model v5.2
Civilization Dynamics Engine
============================================================

v5.2 新增：

1. 时间演化模型
2. 级联传播
3. Civilization Resilience R
4. System Entropy S
5. AI Autonomy U
6. Infrastructure Coupling
7. Recovery Dynamics
8. Shock Propagation
9. Second-order / Third-order effects
10. Monte Carlo Civilization Experiments
11. Stability Index
12. Civilization Phase Detection

安全说明：
本系统是虚拟世界模型。
所有 Cyber Event 都是抽象模拟，
不会执行真实网络攻击、扫描、漏洞利用、
C2、Botnet 或 BGP 操作。
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any
import random
import json
import math


# ============================================================
# VERSION
# ============================================================

MODEL_NAME = "JAE EARTH ONLINE"
MODEL_VERSION = "5.2"


# ============================================================
# ENUM
# ============================================================

class NodeType(Enum):

    POWER = "power"
    AI = "ai"
    CLOUD = "cloud"
    TELECOM = "telecom"
    FACTORY = "factory"
    LOGISTICS = "logistics"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    GOVERNMENT = "government"


class ShockType(Enum):

    CYBER = "cyber"
    ENERGY = "energy"
    ECONOMIC = "economic"
    SUPPLY_CHAIN = "supply_chain"
    AI = "ai"
    CLIMATE = "climate"


class CivilizationPhase(Enum):

    STABLE = "stable"
    STRESSED = "stressed"
    CRITICAL = "critical"
    CASCADING = "cascading"
    RECOVERING = "recovering"
    COLLAPSE = "collapse"


# ============================================================
# WORLD STATE
# ============================================================

@dataclass
class WorldState:

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    ai_capability: float = 0.70

    ai_compute: float = 0.70

    ai_dependency: float = 0.50

    ai_security: float = 0.70

    # AI Autonomy U
    ai_autonomy: float = 0.40

    # --------------------------------------------------------
    # Energy
    # --------------------------------------------------------

    energy_capacity: float = 0.80

    energy_security: float = 0.75

    energy_demand: float = 0.60

    # --------------------------------------------------------
    # Economy
    # --------------------------------------------------------

    gdp: float = 100.0

    economic_growth: float = 0.03

    inflation: float = 0.03

    capital_flow: float = 0.50

    # --------------------------------------------------------
    # Manufacturing
    # --------------------------------------------------------

    manufacturing: float = 0.70

    automation: float = 0.60

    # --------------------------------------------------------
    # Logistics
    # --------------------------------------------------------

    logistics: float = 0.75

    supply_chain: float = 0.75

    supply_chain_risk: float = 0.25

    # --------------------------------------------------------
    # Cyber
    # --------------------------------------------------------

    cyber_threat: float = 0.30

    cyber_defense: float = 0.70

    # --------------------------------------------------------
    # Civilization
    # --------------------------------------------------------

    civilization_health: float = 0.75

    # Civilization resilience R
    resilience_R: float = 0.70

    # System entropy S
    entropy_S: float = 0.30

    # --------------------------------------------------------
    # Time
    # --------------------------------------------------------

    timestep: int = 0

    # --------------------------------------------------------
    # Phase
    # --------------------------------------------------------

    phase: str = CivilizationPhase.STABLE.value

    # --------------------------------------------------------
    # Clamp
    # --------------------------------------------------------

    def clamp(self):

        fields = [

            "ai_capability",
            "ai_compute",
            "ai_dependency",
            "ai_security",
            "ai_autonomy",

            "energy_capacity",
            "energy_security",
            "energy_demand",

            "economic_growth",
            "inflation",
            "capital_flow",

            "manufacturing",
            "automation",

            "logistics",
            "supply_chain",
            "supply_chain_risk",

            "cyber_threat",
            "cyber_defense",

            "civilization_health",
            "resilience_R",
            "entropy_S"

        ]

        for field in fields:

            value = getattr(
                self,
                field
            )

            value = max(
                0.0,
                min(1.0, value)
            )

            setattr(
                self,
                field,
                value
            )

        self.gdp = max(
            0.0,
            self.gdp
        )


# ============================================================
# INFRASTRUCTURE NODE
# ============================================================

@dataclass
class InfrastructureNode:

    node_id: str

    name: str

    node_type: NodeType

    importance: float

    health: float = 1.0

    security: float = 0.70

    recovery_rate: float = 0.05

    energy_dependency: float = 0.50

    ai_dependency: float = 0.30

    supply_dependency: float = 0.50

    economic_dependency: float = 0.50

    active: bool = True

    stressed: bool = False


# ============================================================
# DEPENDENCY EDGE
# ============================================================

@dataclass
class Dependency:

    source: str

    target: str

    strength: float

    dependency_type: str


# ============================================================
# SHOCK
# ============================================================

@dataclass
class Shock:

    shock_id: str

    source: str

    target: str

    shock_type: ShockType

    intensity: float

    timestep: int

    remaining: float = 1.0


# ============================================================
# INFRASTRUCTURE GRAPH
# ============================================================

class InfrastructureGraph:

    def __init__(self):

        self.nodes: Dict[
            str,
            InfrastructureNode
        ] = {}

        self.dependencies: List[
            Dependency
        ] = []

    # --------------------------------------------------------

    def add_node(
        self,
        node: InfrastructureNode
    ):

        self.nodes[
            node.node_id
        ] = node

    # --------------------------------------------------------

    def connect(
        self,
        source: str,
        target: str,
        strength: float,
        dependency_type: str
    ):

        self.dependencies.append(

            Dependency(

                source=source,

                target=target,

                strength=strength,

                dependency_type=
                    dependency_type

            )
        )

    # --------------------------------------------------------

    def outgoing(
        self,
        node_id: str
    ):

        return [

            d

            for d in self.dependencies

            if d.source == node_id

        ]

    # --------------------------------------------------------

    def health(self):

        if not self.nodes:

            return 0.0

        numerator = sum(

            n.health *
            n.importance

            for n in self.nodes.values()

        )

        denominator = sum(

            n.importance

            for n in self.nodes.values()

        )

        return numerator / denominator


# ============================================================
# SHOCK ENGINE
# ============================================================

class ShockEngine:

    def __init__(
        self,
        graph: InfrastructureGraph
    ):

        self.graph = graph

        self.shocks: List[
            Shock
        ] = []

        self.counter = 0

    # --------------------------------------------------------

    def create_shock(
        self,
        source: str,
        target: str,
        shock_type: ShockType,
        intensity: float,
        timestep: int
    ):

        self.counter += 1

        shock = Shock(

            shock_id=
                f"SHOCK-{self.counter:06d}",

            source=source,

            target=target,

            shock_type=shock_type,

            intensity=max(
                0.0,
                min(1.0, intensity)
            ),

            timestep=timestep

        )

        self.shocks.append(shock)

        return shock


# ============================================================
# CASCADE ENGINE
# ============================================================

class CascadeEngine:

    """
    文明级级联传播。

    Node A 受损
        ↓
    Node B 依赖 A
        ↓
    B 健康下降
        ↓
    B 继续影响 C
        ↓
    C 继续传播
    """

    def __init__(
        self,
        graph: InfrastructureGraph
    ):

        self.graph = graph

    # --------------------------------------------------------

    def propagate(
        self,
        affected: Dict[str, float]
    ):

        new_damage = {}

        for node_id, damage in affected.items():

            for dependency in \
                self.graph.outgoing(node_id):

                target = self.graph.nodes.get(
                    dependency.target
                )

                if target is None:

                    continue

                cascade_damage = (

                    damage

                    * dependency.strength

                    * 0.20

                )

                if cascade_damage <= 0:

                    continue

                new_damage[
                    target.node_id
                ] = (

                    new_damage.get(
                        target.node_id,
                        0.0
                    )

                    + cascade_damage

                )

        return new_damage


# ============================================================
# RECOVERY ENGINE
# ============================================================

class RecoveryEngine:

    def __init__(
        self,
        graph: InfrastructureGraph
    ):

        self.graph = graph

    # --------------------------------------------------------

    def recover(
        self,
        world: WorldState
    ):

        recovery_multiplier = (

            0.50

            + world.resilience_R

            * 0.50

        )

        for node in self.graph.nodes.values():

            if node.health >= 1.0:

                continue

            recovery = (

                node.recovery_rate

                * recovery_multiplier

            )

            node.health += recovery

            node.health = min(
                1.0,
                node.health
            )

            if node.health > 0.70:

                node.stressed = False


# ============================================================
# RESILIENCE MODEL
# ============================================================

class ResilienceModel:

    """
    R = 防御能力
        × 恢复能力
        × 冗余能力
        × 系统健康

    简化文明韧性函数。
    """

    def calculate(
        self,
        world: WorldState,
        graph: InfrastructureGraph
    ):

        infrastructure_health = \
            graph.health()

        defense = \
            world.cyber_defense

        recovery = \
            world.resilience_R

        redundancy = (
            1.0 -
            world.supply_chain_risk
        )

        R = (

            infrastructure_health
            * 0.30

            + defense
            * 0.25

            + recovery
            * 0.25

            + redundancy
            * 0.20

        )

        return max(
            0.0,
            min(1.0, R)
        )


# ============================================================
# ENTROPY MODEL
# ============================================================

class EntropyModel:

    """
    S ↑

    表示：

    系统不确定性
    失序程度
    资源浪费
    网络脆弱性
    供应链摩擦
    """

    def calculate(
        self,
        world: WorldState,
        graph: InfrastructureGraph
    ):

        infrastructure_damage = (
            1.0 -
            graph.health()
        )

        cyber_entropy = (
            world.cyber_threat
            * 0.25
        )

        supply_entropy = (
            world.supply_chain_risk
            * 0.25
        )

        geopolitical_entropy = (
            world.inflation
            * 0.10
            +
            world.capital_flow * 0.05
        )

        S = (

            infrastructure_damage
            * 0.30

            + cyber_entropy

            + supply_entropy

            + geopolitical_entropy

        )

        return max(
            0.0,
            min(1.0, S)
        )


# ============================================================
# AI AUTONOMY MODEL
# ============================================================

class AIAutonomyModel:

    """
    U = AI 自主性

    U ↑

    AI：

    工具
      ↓
    Agent
      ↓
    Autonomous System
      ↓
    Civilization Infrastructure
    """

    def evolve(
        self,
        world: WorldState
    ):

        growth = (

            world.ai_capability

            * world.ai_compute

            * 0.002

        )

        dependency_pressure = (

            world.ai_dependency
            * 0.001

        )

        security_constraint = (

            world.ai_security
            * 0.001

        )

        world.ai_autonomy += (

            growth
            + dependency_pressure
            - security_constraint

        )

        world.ai_autonomy = max(
            0.0,
            min(
                1.0,
                world.ai_autonomy
            )
        )


# ============================================================
# CIVILIZATION DYNAMICS
# ============================================================

class CivilizationDynamics:

    def __init__(self):

        self.resilience = \
            ResilienceModel()

        self.entropy = \
            EntropyModel()

        self.ai = \
            AIAutonomyModel()

    # --------------------------------------------------------

    def update(
        self,
        world: WorldState,
        graph: InfrastructureGraph
    ):

        # AI演化

        self.ai.evolve(
            world
        )

        # 韧性

        world.resilience_R = \
            self.resilience.calculate(
                world,
                graph
            )

        # 熵

        world.entropy_S = \
            self.entropy.calculate(
                world,
                graph
            )

        # ----------------------------------------------------
        # Civilization Health
        # ----------------------------------------------------

        infrastructure_health = \
            graph.health()

        health = (

            infrastructure_health
            * 0.30

            + world.energy_security
            * 0.15

            + world.supply_chain
            * 0.15

            + world.cyber_defense
            * 0.10

            + world.resilience_R
            * 0.15

            + world.social_stability
            * 0.10

            + world.ai_security
            * 0.05

        )

        # 熵惩罚

        health -= (
            world.entropy_S
            * 0.10
        )

        world.civilization_health = max(
            0.0,
            min(1.0, health)
        )

        # ----------------------------------------------------
        # Civilization Phase
        # ----------------------------------------------------

        if world.civilization_health > 0.70:

            world.phase = \
                CivilizationPhase.STABLE.value

        elif world.civilization_health > 0.50:

            world.phase = \
                CivilizationPhase.STRESSED.value

        elif world.civilization_health > 0.30:

            world.phase