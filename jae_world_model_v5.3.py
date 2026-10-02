"""
============================================================
JAE EARTH ONLINE
ONE WORLD MODEL v5.3
Civilization Evolution Laboratory
============================================================

研究问题：

    什么样的世界结构能够长期存活？

v5.3 新增：

1. Civilization Fitness
2. Long-term Survival
3. Evolutionary Selection
4. Parameter Mutation
5. Population of Worlds
6. World Genome
7. Civilization Diversity
8. Collapse Detection
9. Generational Evolution
10. Long-term Civilization Experiment

安全说明：
本模型仅进行抽象文明系统模拟。
Cyber、AI、能源、经济等均为数学变量，
不会执行真实网络攻击或现实基础设施操作。
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
import random
import copy
import json


# ============================================================
# VERSION
# ============================================================

MODEL_NAME = "JAE EARTH ONLINE"
MODEL_VERSION = "5.3"


# ============================================================
# WORLD GENOME
# ============================================================

@dataclass
class WorldGenome:

    """
    一个世界的“基因组”。

    它决定文明的底层结构。
    """

    # --------------------------------------------------------
    # AI
    # --------------------------------------------------------

    ai_capability: float = 0.70

    ai_autonomy: float = 0.40

    ai_dependency: float = 0.50

    ai_security: float = 0.70

    # --------------------------------------------------------
    # ENERGY
    # --------------------------------------------------------

    energy_redundancy: float = 0.70

    energy_security: float = 0.75

    energy_efficiency: float = 0.60

    # --------------------------------------------------------
    # ECONOMY
    # --------------------------------------------------------

    economic_diversity: float = 0.70

    economic_resilience: float = 0.65

    capital_flexibility: float = 0.60

    # --------------------------------------------------------
    # SUPPLY CHAIN
    # --------------------------------------------------------

    supply_diversity: float = 0.70

    local_production: float = 0.50

    logistics_redundancy: float = 0.65

    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    information_redundancy: float = 0.70

    network_decentralization: float = 0.60

    # --------------------------------------------------------
    # GOVERNANCE
    # --------------------------------------------------------

    institutional_adaptability: float = 0.60

    decision_speed: float = 0.55

    coordination: float = 0.70

    # --------------------------------------------------------
    # SOCIAL
    # --------------------------------------------------------

    social_cohesion: float = 0.65

    cultural_diversity: float = 0.60

    # --------------------------------------------------------
    # SCIENCE
    # --------------------------------------------------------

    scientific_capacity: float = 0.70

    experimentation_rate: float = 0.60


# ============================================================
# WORLD STATE
# ============================================================

@dataclass
class EvolutionWorld:

    genome: WorldGenome

    age: int = 0

    health: float = 1.0

    resilience: float = 0.70

    entropy: float = 0.30

    adaptability: float = 0.60

    diversity: float = 0.60

    stability: float = 0.70

    collapse_risk: float = 0.20

    alive: bool = True

    shocks_survived: int = 0

    shocks_received: int = 0

    recovery_count: int = 0

    fitness: float = 0.0


# ============================================================
# CLAMP
# ============================================================

def clamp(
    value: float
) -> float:

    return max(
        0.0,
        min(
            1.0,
            value
        )
    )


# ============================================================
# CIVILIZATION SIMULATOR
# ============================================================

class CivilizationSimulator:

    def __init__(
        self,
        world: EvolutionWorld
    ):

        self.world = world

    # ========================================================
    # STRUCTURAL METRICS
    # ========================================================

    def calculate_resilience(self):

        g = self.world.genome

        redundancy = (

            g.energy_redundancy
            + g.logistics_redundancy
            + g.information_redundancy
            + g.supply_diversity

        ) / 4

        adaptability = (

            g.institutional_adaptability
            + g.scientific_capacity
            + g.experimentation_rate

        ) / 3

        decentralization = (

            g.network_decentralization
            + g.economic_diversity
            + g.cultural_diversity

        ) / 3

        self.world.resilience = clamp(

            redundancy * 0.40

            + adaptability * 0.35

            + decentralization * 0.25

        )

    # ========================================================

    def calculate_adaptability(self):

        g = self.world.genome

        self.world.adaptability = clamp(

            g.institutional_adaptability
            * 0.30

            + g.scientific_capacity
            * 0.25

            + g.experimentation_rate
            * 0.20

            + g.decision_speed
            * 0.10

            + g.coordination
            * 0.15

        )

    # ========================================================

    def calculate_diversity(self):

        g = self.world.genome

        self.world.diversity = clamp(

            g.economic_diversity
            * 0.25

            + g.supply_diversity
            * 0.25

            + g.cultural_diversity
            * 0.20

            + g.energy_redundancy
            * 0.15

            + g.information_redundancy
            * 0.15

        )

    # ========================================================
    # AI EFFECT
    # ========================================================

    def ai_dynamics(self):

        g = self.world.genome

        ai_benefit = (

            g.ai_capability
            * g.scientific_capacity

        )

        ai_risk = (

            g.ai_autonomy
            * g.ai_dependency
            * (1.0 - g.ai_security)

        )

        self.world.health += (

            ai_benefit
            * 0.001

        )

        self.world.entropy += (

            ai_risk
            * 0.001

        )

    # ========================================================
    # SYSTEM ENTROPY
    # ========================================================

    def calculate_entropy(self):

        g = self.world.genome

        centralization = (

            1.0
            - g.network_decentralization

        )

        dependency = (

            g.ai_dependency
            * 0.5

            + (1.0 - g.supply_diversity)
            * 0.5

        )

        coordination_cost = (

            abs(
                g.decision_speed
                - g.coordination
            )
            * 0.2

        )

        self.world.entropy += (

            centralization
            * 0.001

            + dependency
            * 0.001

            + coordination_cost
            * 0.001

        )

        self.world.entropy = clamp(
            self.world.entropy
        )

    # ========================================================
    # NATURAL EVOLUTION
    # ========================================================

    def natural_growth(self):

        growth = (

            self.world.adaptability
            * self.world.resilience
            * 0.002

        )

        self.world.health += growth

        self.world.health = clamp(
            self.world.health
        )

    # ========================================================
    # SHOCK
    # ========================================================

    def shock(self):

        g = self.world.genome

        # 随机文明冲击

        intensity = random.uniform(
            0.05,
            0.35
        )

        self.world.shocks_received += 1

        resistance = (

            self.world.resilience
            * 0.50

            + g.energy_security
            * 0.15

            + g.economic_resilience
            * 0.15

            + g.logistics_redundancy
            * 0.10

            + g.information_redundancy
            * 0.10

        )

        damage = (

            intensity
            * (1.0 - resistance)

        )

        self.world.health -= damage

        if resistance > intensity:

            self.world.shocks_survived += 1

        self.world.collapse_risk += (

            damage
            * 0.50

        )

    # ========================================================
    # RECOVERY
    # ========================================================

    def recover(self):

        recovery = (

            self.world.resilience
            * self.world.adaptability
            * 0.01

        )

        if self.world.health < 1.0:

            self.world.health += recovery

            self.world.recovery_count += 1

        self.world.health = clamp(
            self.world.health
        )

    # ========================================================
    # COLLAPSE CHECK
    # ========================================================

    def collapse_check(self):

        if self.world.health <= 0.05:

            self.world.alive = False

            return True

        if self.world.entropy >= 0.98:

            self.world.alive = False

            return True

        if self.world.collapse_risk >= 0.98:

            self.world.alive = False

            return True

        return False

    # ========================================================
    # STEP
    # ========================================================

    def step(self):

        if not self.world.alive:

            return

        self.world.age += 1

        # 结构计算

        self.calculate_resilience()

        self.calculate_adaptability()

        self.calculate_diversity()

        # AI

        self.ai_dynamics()

        # 熵

        self.calculate_entropy()

        # 正常发展

        self.natural_growth()

        # 随机冲击

        if random.random() < 0.04:

            self.shock()

        # 恢复

        self.recover()

        # 崩溃检测

        self.collapse_check()

        # 稳定性

        self.world.stability = clamp(

            self.world.health
            * 0.40

            + self.world.resilience
            * 0.25

            + self.world.adaptability
            * 0.20

            + self.world.diversity
            * 0.15

            - self.world.entropy
            * 0.10

        )


# ============================================================
# FITNESS
# ============================================================

class FitnessEngine:

    """
    不问：

        “哪个世界最好？”

    而问：

        “哪些结构在长期演化中
         更容易继续存在？”
    """

    def calculate(
        self,
        world: EvolutionWorld,
        simulation_steps: int
    ):

        longevity = (

            world.age
            / simulation_steps

        )

        survival = (

            1.0
            if world.alive
            else 0.0

        )

        resilience = \
            world.resilience

        adaptability = \
            world.adaptability

        diversity = \
            world.diversity

        entropy_penalty = \
            world.entropy

        collapse_penalty = \
            world.collapse_risk

        recovery_bonus = clamp(

            world.recovery_count
            / max(
                1,
                world.shocks_received
            )

        )

        fitness = (

            longevity
            * 0.25

            + survival
            * 0.20

            + resilience
            * 0.20

            + adaptability
            * 0.15

            + diversity
            * 0.10

            + recovery_bonus
            * 0.10

            - entropy_penalty
            * 0.15

            - collapse_penalty
            * 0.10

        )

        world.fitness = fitness

        return fitness


# ============================================================
# MUTATION ENGINE
# ============================================================

class MutationEngine:

    """
    世界基因发生微小变化。

    注意：

    不是人为设计答案。

    而是：

        随机变化
             ↓
        长期运行
             ↓
        观察结果
             ↓
        保留能够持续存在的结构
    """

    MUTATION_RATE = 0.08

    def mutate(
        self,
        genome: WorldGenome
    ):

        child = copy.deepcopy(
            genome
        )
"vulnerability_ecosystem": {
  "bounty_program_openness": 0.72,
  "responsible_disclosure_strength": 0.68,
  "ai_agent_risk": 0.74,
  "prompt_injection_pressure": 0.69,
  "supply_chain_vuln_discovery": 0.71,
  "proof_verification_backlog": 0.71,
  "mathematical_certainty": 0.46,
  "trust_chain_friction": 0.58,
  "bounty_spam_noise": 0.63,
  "high_value_vuln_scarcity": 0.57
}
