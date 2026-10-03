"""
=========================================================
JAE UNIFIED WORLD MODEL v7.0 — FINAL
Multi-Scale Civilization Simulation Engine
=========================================================

知识集成（可计算形式，非装饰性引用）：
    [K01] 控制论      Wiener 1948      → FeedbackEngine 稳定性阻尼
    [K02] 复杂系统    Santa Fe 1980s   → 临界阈值 + 涌现
    [K03] 演化博弈    Axelrod 1984     → Layer0 reward shaping
    [K04] 社会选择    Arrow 1951       → MesoAggregator 聚合张力
    [K05] 网络科学    Barabási 1999    → 非对称 CouplingEngine
    [K06] 信息论      Shannon 1948     → 状态熵度量
    [K07] 耗散结构    Prigogine 1977   → 能量账本 (energy ledger)
    [K08] 生态学      Lotka 1925       → 资源再生动力学
    [K09] 分配正义    Gini 1912        → 不平等度量
    [K10] 有限理性    Simon 1955       → 有界状态空间编码
    [K11] AI 对齐     Bostrom 2014     → H(控制缺口) / I(不可逆)
    [K12] 多层级选择  Wilson 1994      → 微观→中观→宏观耦合

诚实声明：
    "全人类知识"是不可达的建模目标。本文件集成的是 12 个可形式化、
    可计算、可证伪的跨学科框架。任何声称"全知"的模型都违背了建模
    的第一原则——知道自己丢掉了什么。
=========================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from collections import deque, defaultdict
from enum import Enum
from typing import Dict, List, Optional, Tuple
import json, math, random, csv
from copy import deepcopy


# ═════════════════════════════════════════════════════════
# §1  通用工具
# ═════════════════════════════════════════════════════════

def clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))

def gini(xs: List[float]) -> float:
    """[K09] Gini 系数：0 = 完全平等，1 = 完全不平等"""
    xs = sorted(max(0.0, float(x)) for x in xs)
    n = len(xs)
    total = sum(xs)
    if n == 0 or total == 0:
        return 0.0
    return 2 * sum((i + 1) * x for i, x in enumerate(xs)) / (n * total) - (n + 1) / n

def shannon_entropy(counts: Dict) -> float:
    """[K06] 香农熵：状态分布的不确定性"""
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return round(h, 4)

def lotka_regen(current: float, cap: float, rate: float) -> float:
    """[K08] 逻辑斯蒂再生：r * x * (1 - x/K)"""
    return current + rate * current * (1 - current / cap)


# ═════════════════════════════════════════════════════════
# §2  LAYER 0 · SUBSTRATE (v3 强化版)
# ═════════════════════════════════════════════════════════

ACTIONS = ("gather", "share", "attack", "rest", "explore")


@dataclass
class AgentState:
    id: int
    x: int
    y: int
    energy: float = 100.0
    resource: float = 0.0
    health: float = 100.0
    alive: bool = True
    age: int = 0
    # v7.0：trust 现在真正参与决策
    trust: Dict[int, float] = field(default_factory=dict)
    memory: deque = field(default_factory=lambda: deque(maxlen=8))


class SubstrateWorld:
    """[K07] 开放耗散系统：能量从资源流入，通过行动流出"""

    def __init__(self, n: int = 30, w: int = 24, h: int = 24, seed: int = 2026):
        self.rng = random.Random(seed)
        self.w, self.h, self.t = w, h, 0
        self.resources = {(x, y): self.rng.uniform(2, 10)
                          for x in range(w) for y in range(h)}
        self.cap = 10.0
        self.agents = {i: AgentState(
            i, self.rng.randrange(w), self.rng.randrange(h))
            for i in range(n)}
        for a in self.agents.values():
            a.trust = {j: 0.5 for j in self.agents if j != a.id}
        # v7.0 [K03]：宏观→微观反馈的奖励偏置
        self.reward_bias = {"share": 2.0, "attack": -1.5}
        self.events: List[Tuple] = []

    # -------------------------------------------------
    # OBSERVATION
    # -------------------------------------------------

    def obs(self, i: int) -> Dict:
        a = self.agents[i]
        nearby = []
        for b in self.agents.values():
            if b.id == i or not b.alive:
                continue
            d = abs(a.x - b.x) + abs(a.y - b.y)
            if d <= 2:
                nearby.append((
                    b.id, d, b.energy, b.resource,
                    a.trust.get(b.id, 0.5), b.health,
                ))
        return {
            "x": a.x, "y": a.y,
            "energy": a.energy, "resource": a.resource,
            "health": a.health, "age": a.age,
            "local": self.resources[(a.x, a.y)],
            "nearby": nearby,
        }

    # -------------------------------------------------
    # STATE ENCODING (v7.0: 27 → 243)
    # -------------------------------------------------

    @staticmethod
    def state(o: Dict) -> str:
        """[K10] 有限理性：状态空间 = 3^5 = 243"""
        e = "L" if o["energy"] < 20 else "M" if o["energy"] < 60 else "H"
        r = "P" if o["local"] < 4 else "M" if o["local"] < 7 else "R"

        near = o["nearby"]
        if not near:
            n, t, h = "0", "X", "X"
        else:
            n = "F" if len(near) <= 2 else "M"
            avg_t = sum(item[4] for item in near) / len(near)
            avg_h = sum(item[5] for item in near) / len(near)
            t = "W" if avg_t < 0.35 else "M" if avg_t < 0.65 else "S"
            h = "W" if avg_h < 40 else "M" if avg_h < 80 else "S"

        return f"{e}|{r}|{n}|{t}|{h}"

    # -------------------------------------------------
    # TARGET SELECTION (v7.0: trust-aware)
    # -------------------------------------------------

    def nearest(
        self,
        a: AgentState,
        min_trust: Optional[float] = None,
        max_trust: Optional[float] = None,
    ) -> Optional[AgentState]:
        cands = []
        for b in self.agents.values():
            if b.id == a.id or not b.alive:
                continue
            d = abs(a.x - b.x) + abs(a.y - b.y)
            if d > 2:
                continue
            tr = a.trust.get(b.id, 0.5)
            if min_trust is not None and tr < min_trust:
                continue
            if max_trust is not None and tr > max_trust:
                continue
            cands.append((d, b))
        return min(cands, key=lambda z: z[0])[1] if cands else None

    # -------------------------------------------------
    # ACTION RESOLUTION
    # -------------------------------------------------

    def act(self, i: int, action: str) -> Tuple[float, Dict]:
        a = self.agents[i]
        e0, r0 = a.energy, a.resource
        ev = []
        a.energy -= 1.0
        a.age += 1

        if action == "gather":
            p = (a.x, a.y)
            q = min(self.resources[p], self.rng.uniform(1, 5))
            self.resources[p] -= q
            a.resource += q
            a.energy += 0.6 * q                      # v7.0: 0.4 → 0.6
            ev.append(("gather", q, None))

        elif action == "share":
            b = self.nearest(a, min_trust=0.3)       # v7.0: 只分享给信任 ≥0.3
            if b and a.resource >= 1:
                q = min(2, a.resource)
                a.resource -= q
                b.resource += q
                a.trust[b.id] = min(1.0, a.trust.get(b.id, 0.5) + 0.08)
                b.trust[a.id] = min(1.0, b.trust.get(a.id, 0.5) + 0.05)
                ev.append(("share", q, b.id))

        elif action == "attack":
            b = self.nearest(a, max_trust=0.7)       # v7.0: 只攻击信任 ≤0.7
            if b:
                d = self.rng.uniform(5, 20)
                b.health -= d
                a.energy -= 2
                a.trust[b.id] = max(0.0, a.trust.get(b.id, 0.5) - 0.25)
                b.trust[a.id] = max(0.0, b.trust.get(a.id, 0.5) - 0.30)
                ev.append(("attack", d, b.id))

        elif action == "rest":
            q = self.rng.uniform(2, 5)
            a.energy += q
            # v7.0: rest 消耗 0.5 资源（"维持成本"），修复 v3 的免费午餐
            a.resource = max(0.0, a.resource - 0.5)
            ev.append(("rest", q, None))

        elif action == "explore":
            dx, dy = self.rng.choice(((-1, 0), (1, 0), (0, -1), (0, 1)))
            a.x = max(0, min(self.w - 1, a.x + dx))
            a.y = max(0, min(self.h - 1, a.y + dy))
            a.energy -= 0.5
            ev.append(("explore", 1, None))

        if a.energy <= 0 or a.health <= 0:
            a.alive = False
            ev.append(("death", 1, None))

        # --- REWARD SHAPING ---
        reward = 0.5 * (a.energy - e0) + (a.resource - r0)
        if action == "share":
            reward += self.reward_bias["share"]
        if action == "attack":
            reward += self.reward_bias["attack"]
        if not a.alive:
            reward -= 30
        if a.energy < 10:
            reward -= 2

        self.events += [(self.t, i, *e) for e in ev]
        a.memory.append((self.t, action, round(reward, 3)))
        return reward, self.obs(i)

    # -------------------------------------------------
    # TICK (resource regeneration)
    # -------------------------------------------------

    def tick(self) -> None:
        self.t += 1
        for p in self.resources:
            self.resources[p] = min(
                self.cap, lotka_regen(self.resources[p], self.cap, 0.02)
            )

    # -------------------------------------------------
    # WINDOWED METRICS
    # -------------------------------------------------

    def metrics(self, window: int = 50) -> Dict:
        alive = [a for a in self.agents.values() if a.alive]
        recent = self.events[-window * len(self.agents):] if self.events else []
        total = max(1, len(recent))

        shares = sum(1 for e in recent if len(e) > 2 and e[2] == "share")
        attacks = sum(1 for e in recent if len(e) > 2 and e[2] == "attack")

        rs = [a.resource for a in alive]
        trust_vals = [
            v for a in alive for v in a.trust.values()
        ] or [0.5]

        # [K06] 状态熵
        state_counts = defaultdict(int)
        for a in alive:
            state_counts[self.state(self.obs(a.id))] += 1

        return {
            "step": self.t,
            "alive": len(alive),
            "avg_energy": sum(a.energy for a in alive) / len(alive) if alive else 0,
            "avg_resource": sum(rs) / len(rs) if rs else 0,
            "cooperation_rate": shares / total,
            "conflict_rate": attacks / total,
            "gini": gini(rs),
            "avg_trust": sum(trust_vals) / len(trust_vals),
            "state_entropy": shannon_entropy(state_counts),
        }


class SubstrateLearner:
    """[K03][K10] Q-learning with bounded rationality"""

    def __init__(self, seed: int = 0):
        self.r = random.Random(seed)
        self.q: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {a: 0.0 for a in ACTIONS}
        )
        self.alpha = 0.10
        self.gamma = 0.92
        self.eps = 0.25
        self.td_history: deque = deque(maxlen=200)

    def act(self, s: str) -> str:
        if self.r.random() < self.eps:
            return self.r.choice(ACTIONS)
        return max(ACTIONS, key=lambda a: self.q[s][a])

    def update(self, s: str, a: str, r: float, ns: str) -> float:
        td = r + self.gamma * max(self.q[ns].values()) - self.q[s][a]
        self.q[s][a] += self.alpha * td
        self.td_history.append(td)
        return td

    def decay(self) -> None:
        self.eps = max(0.03, self.eps * 0.9995)

    def convergence(self) -> float:
        """T 在微观层的类比物：TD 误差的滑动标准差"""
        if len(self.td_history) < 10:
            return 0.0
        vals = list(self.td_history)[-50:]
        mu = sum(vals) / len(vals)
        var = sum((v - mu) ** 2 for v in vals) / len(vals)
        return round(math.sqrt(var), 4)


# ═════════════════════════════════════════════════════════
# §3  LAYER 1 · MESO (Cohort 分层)
# ═════════════════════════════════════════════════════════

@dataclass
class Cohort:
    name: str
    size: int
    capacity: float      # 平均资源存量
    cohesion: float      # 平均内部信任
    grievance: float     # 相对剥夺感
    mobilization: float  # 行动倾向（抗议/迁移/攻击）


class MesoAggregator:
    """[K04][K09][K12] 从个体聚合出中层结构

    Arrow 的不可能性定理警告我们：个体偏好聚合不产生一致的集体偏好。
    本层不假装解决了这个问题——它只是暴露这个张力：我们跟踪"聚合后的
    压力"，而不是"聚合后的意志"。
    """

    def aggregate(self, world: SubstrateWorld) -> Dict[str, Cohort]:
        alive = [a for a in world.agents.values() if a.alive]
        if len(alive) < 3:
            return {}

        alive.sort(key=lambda a: a.resource)
        n = len(alive)
        tiers = {
            "lower": alive[: max(1, n // 3)],
            "middle": alive[max(1, n // 3): max(2, 2 * n // 3)],
            "upper": alive[max(2, 2 * n // 3):],
        }

        max_r = max(a.resource for a in alive) or 1.0
        cohorts: Dict[str, Cohort] = {}

        for name, members in tiers.items():
            if not members:
                continue
            avg_r = sum(a.resource for a in members) / len(members)
            trust_pairs = [v for a in members for v in a.trust.values()]
            avg_trust = sum(trust_pairs) / len(trust_pairs) if trust_pairs else 0.5
            grievance = max(0.0, (max_r - avg_r) / max_r)

            # mobilization: 剥夺感 × (1 - 信任) × 规模因子
            mobilization = grievance * (1 - avg_trust) * min(1.0, len(members) / 10)

            cohorts[name] = Cohort(
                name=name,
                size=len(members),
                capacity=round(avg_r, 3),
                cohesion=round(avg_trust, 3),
                grievance=round(grievance, 3),
                mobilization=round(mobilization, 3),
            )

        return cohorts

    def coupling_pressure(self, cohorts: Dict[str, Cohort]) -> Dict[str, float]:
        """[K12] 中观 → 宏观：下层的动员 vs 上层的凝聚"""
        if not cohorts:
            return {"mobilization": 0.0, "cohesion": 0.0}

        total = sum(c.size for c in cohorts.values()) or 1
        mob = sum(c.mobilization * c.size for c in cohorts.values()) / total
        coh = sum(c.cohesion * c.size for c in cohorts.values()) / total
        return {"mobilization": round(mob, 4), "cohesion": round(coh, 4)}


# ═════════════════════════════════════════════════════════
# §4  LAYER 2 · MACRO (v6.1 + 4 留白补全)
# ═════════════════════════════════════════════════════════

class WorldSystem(str, Enum):
    FINANCE = "金融"
    ENERGY = "能源"
    SUPPLY_CHAIN = "供应链"
    MILITARY = "军事"
    INFORMATION = "信息"


SYSTEMS = list(WorldSystem)

ASI_WEIGHTS = {
    "U": 0.18, "A": 0.12, "C": 0.08, "N": 0.08, "D": 0.07,
    "H": 0.10, "R": 0.15, "X": 0.12, "I": 0.10,
}
assert abs(sum(ASI_WEIGHTS.values()) - 1.0) < 1e-9


class ASIZone(str, Enum):
    TOOL = "工具区"
    AGENT = "Agent区"
    CRITICAL = "主体化临界区"
    SUBJECT = "主体化区"
    NETWORK = "主体网络区"


ZONE_BANDS = [
    (ASIZone.TOOL, 0.0, 60.0),
    (ASIZone.AGENT, 60.0, 75.0),
    (ASIZone.CRITICAL, 75.0, 85.0),
    (ASIZone.SUBJECT, 85.0, 92.0),
    (ASIZone.NETWORK, 92.0, 100.0),
]


def classify_asi(score: float) -> ASIZone:
    for zone, _lo, hi in ZONE_BANDS:
        if score < hi:
            return zone
    return ASIZone.NETWORK


class AIPhase(str, Enum):
    TOOL = "Tool"
    AGENT = "Agent"
    CRITICAL = "Critical"
    SUBJECT = "Subject"
    NETWORK = "Network"


PHASE_BY_ZONE = {
    ASIZone.TOOL: AIPhase.TOOL,
    ASIZone.AGENT: AIPhase.AGENT,
    ASIZone.CRITICAL: AIPhase.CRITICAL,
    ASIZone.SUBJECT: AIPhase.SUBJECT,
    ASIZone.NETWORK: AIPhase.NETWORK,
}


def determine_ai_phase(score: float) -> AIPhase:
    return PHASE_BY_ZONE[classify_asi(score)]


@dataclass
class SystemState:
    name: WorldSystem
    U: float; A: float; C: float; N: float; D: float
    H: float; R: float; X: float; I: float
    T: float = 0.0
    F: float = 0.0
    resources: float = 100.0
    stability: float = 100.0
    dependency: float = 0.0
    stress: float = 0.0
    history: List[Dict] = field(default_factory=list)
    _last_asi: Optional[float] = field(default=None, repr=False, compare=False)

    def as_dict(self):
        d = asdict(self)
        d["name"] = self.name.value
        d.pop("_last_asi", None)
        return d


def initial_system_states() -> Dict[WorldSystem, SystemState]:
    return {
        WorldSystem.FINANCE: SystemState(
            WorldSystem.FINANCE, U=78, A=76, C=90, N=94, D=94,
            H=51, R=65, X=96, I=88),
        WorldSystem.ENERGY: SystemState(
            WorldSystem.ENERGY, U=70, A=68, C=82, N=82, D=80,
            H=38, R=57, X=87, I=97),
        WorldSystem.SUPPLY_CHAIN: SystemState(
            WorldSystem.SUPPLY_CHAIN, U=84, A=80, C=84, N=90, D=96,
            H=58, R=72, X=91, I=63),
        WorldSystem.MILITARY: SystemState(
            WorldSystem.MILITARY, U=76, A=73, C=87, N=85, D=89,
            H=35, R=69, X=88, I=95),
        WorldSystem.INFORMATION: SystemState(
            WorldSystem.INFORMATION, U=90, A=69, C=88, N=98, D=99,
            H=55, R=78, X=94, I=58),
    }


class ASIEngine:
    """[K11] 主体化指数

    v7.0 变更：T（主体化速度）现在作为加速度项参与评分（限幅 ±2）。
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        if weights is None:
            self.weights = deepcopy(ASI_WEIGHTS)
        else:
            total = sum(weights.values())
            self.weights = ({k: v / total for k, v in weights.items()}
                            if total > 0 else deepcopy(ASI_WEIGHTS))

    def calculate(self, state: SystemState) -> float:
        score = sum(getattr(state, k) * self.weights[k] for k in self.weights)
        # v7.0 [留白3补全]：T 作为加速度项
        score += clip(state.T, -2.0, 2.0) * 0.5
        return round(score, 2)

    def zone(self, state: SystemState) -> ASIZone:
        return classify_asi(self.calculate(state))

    def rank(self, states: Dict[WorldSystem, SystemState]) -> List[Dict]:
        r = [{"system": s.name.value, "ASI": self.calculate(s),
              "zone": self.zone(s).value}
             for s in states.values()]
        return sorted(r, key=lambda x: x["ASI"], reverse=True)


DEFAULT_COUPLING = {
    WorldSystem.FINANCE: {
        WorldSystem.ENERGY: 0.82, WorldSystem.SUPPLY_CHAIN: 0.91,
        WorldSystem.MILITARY: 0.63, WorldSystem.INFORMATION: 0.88},
    WorldSystem.ENERGY: {
        WorldSystem.FINANCE: 0.79, WorldSystem.SUPPLY_CHAIN: 0.86,
        WorldSystem.MILITARY: 0.77, WorldSystem.INFORMATION: 0.66},
    WorldSystem.SUPPLY_CHAIN: {
        WorldSystem.FINANCE: 0.74, WorldSystem.ENERGY: 0.79,
        WorldSystem.MILITARY: 0.72, WorldSystem.INFORMATION: 0.79},
    WorldSystem.MILITARY: {
        WorldSystem.FINANCE: 0.71, WorldSystem.ENERGY: 0.68,
        WorldSystem.SUPPLY_CHAIN: 0.81, WorldSystem.INFORMATION: 0.89},
    WorldSystem.INFORMATION: {
        WorldSystem.FINANCE: 0.82, WorldSystem.ENERGY: 0.71,
        WorldSystem.SUPPLY_CHAIN: 0.84, WorldSystem.MILITARY: 0.93},
}


class CouplingEngine:
    """[K05] 非对称耦合矩阵"""

    def __init__(self, matrix: Optional[Dict] = None):
        self.matrix = deepcopy(matrix if matrix is not None else DEFAULT_COUPLING)

    def systemic_coupling(self, system: WorldSystem) -> float:
        conns = self.matrix.get(system, {})
        if not conns:
            return 0.0
        return round(sum(conns.values()) / len(conns) * 100.0, 2)


class FeedbackEngine:
    """[K01] 带稳定性阻尼的反馈"""

    GAIN_U = 0.03
    GAIN_R = 0.025
    GAIN_X = 0.02
    STABILITY_DAMPING = 0.7

    def calculate_feedback(self, state: SystemState, coupling: float) -> float:
        fb = (state.U / 100) * (state.R / 100) * (state.N / 100) * coupling
        return round(min(fb * 100.0, 100.0), 2)

    def apply_feedback(self, state: SystemState, feedback: float) -> None:
        factor = 1.0 - self.STABILITY_DAMPING * (1.0 - state.stability / 100.0)
        net = feedback * factor
        state.U = clip(state.U + net * self.GAIN_U)
        state.R = clip(state.R + net * self.GAIN_R)
        state.X = clip(state.X + net * self.GAIN_X)


class RecursiveAutonomyEngine:
    def recursion_pressure(self, state: SystemState) -> float:
        return (state.U * state.A * state.R) / 1_000_000.0

    def evolve(self, state: SystemState, steps: int = 1) -> None:
        for _ in range(steps):
            p = self.recursion_pressure(state)
            state.R = clip(state.R + p * 0.5)
            state.N = clip(state.N + p * 0.2)
            state.X = clip(state.X + p * 0.25)


class MacroWorld:
    HISTORY_CAP = 500

    def __init__(self):
        self.time = 0
        self.systems = initial_system_states()
        self.asi = ASIEngine()
        self.coupling = CouplingEngine()
        self.feedback = FeedbackEngine()
        self.recursive = RecursiveAutonomyEngine()
        for s in self.systems.values():
            s._last_asi = self.asi.calculate(s)

    def step(self, meso_pressure: Optional[Dict[str, float]] = None) -> None:
        self.time += 1

        for system, state in self.systems.items():
            coupling = self.coupling.systemic_coupling(system) / 100.0
            fb = self.feedback.calculate_feedback(state, coupling)
            state.F = fb
            self.feedback.apply_feedback(state, fb)
            self.recursive.evolve(state, steps=1)

        self._propagate()
        self._update_stress_stability()
        self._update_resources_dependency()      # [留白1补全]
        self._update_authority_dilution()        # [留白2补全]
        if meso_pressure:
            self._apply_meso_pressure(meso_pressure)
        self._calculate_velocity()

        for state in self.systems.values():
            state.history.append({
                "time": self.time,
                "ASI": self.asi.calculate(state),
                "R": round(state.R, 3),
                "X": round(state.X, 3),
                "stability": round(state.stability, 2),
                "stress": round(state.stress, 2),
            })
            if len(state.history) > self.HISTORY_CAP:
                state.history.pop(0)
            state._last_asi = self.asi.calculate(state)

    def _propagate(self) -> None:
        """v6.1 差值驱动 + v7.0 [留白4补全]：也触及 A / D"""
        cur = {s: self.asi.calculate(st) for s, st in self.systems.items()}
        K = 0.8
        for src in SYSTEMS:
            for tgt in SYSTEMS:
                if src == tgt:
                    continue
                coef = self.coupling.matrix.get(src, {}).get(tgt, 0.0)
                if coef <= 0:
                    continue
                delta = (cur[src] - cur[tgt]) / 100.0
                p = delta * coef * K
                st = self.systems[tgt]
                st.X = clip(st.X + p)
                st.N = clip(st.N + p * 0.5)
                st.A = clip(st.A + p * 0.3)        # v7.0
                st.D = clip(st.D + p * 0.4)        # v7.0

    def _update_stress_stability(self) -> None:
        for state in self.systems.values():
            asi = self.asi.calculate(state)
            target = clip((asi - 70.0) / 30.0 * 100.0)
            state.stress = 0.85 * state.stress + 0.15 * target
            state.stability = clip(
                state.stability - state.stress / 100.0 * 0.8 + 0.1)

    def _update_resources_dependency(self) -> None:
        """[留白1补全]：D 消耗资源，C 恢复资源；X 提升依赖"""
        for state in self.systems.values():
            state.resources = clip(
                state.resources - state.D * 0.001 + state.C * 0.0008)
            state.dependency = clip(state.dependency + state.X * 0.0003)

    def _update_authority_dilution(self) -> None:
        """[留白2补全]：递归自主性 R 越高，权威 A 越被稀释"""
        for state in self.systems.values():
            dilution = max(0.0, state.R - 60.0) / 100.0 * 0.03
            state.A = clip(state.A - dilution)

    def _apply_meso_pressure(self, pressure: Dict[str, float]) -> None:
        """[K12] 中观 → 宏观：动员压力降低稳定性，凝聚提升稳定性"""
        mob = pressure.get("mobilization", 0.0)
        coh = pressure.get("cohesion", 0.0)
        for state in self.systems.values():
            state.stability = clip(state.stability - mob * 0.5 + coh * 0.3)
            state.stress = clip(state.stress + mob * 0.8)

    def _calculate_velocity(self) -> None:
        for state in self.systems.values():
            if state._last_asi is None:
                state.T = 0.0
            else:
                state.T = round(self.asi.calculate(state) - state._last_asi, 4)


# ═════════════════════════════════════════════════════════
# §5  LAYER 3 · META
# ═════════════════════════════════════════════════════════

@dataclass
class Diagnosis:
    time: int
    substrate_alive: int
    macro_mean_asi: float
    macro_max_asi: float
    meso_mobilization: float
    meso_gini: float
    warnings: List[str]


class Observer:
    """[K02] 全局诊断：寻找跨层临界信号"""

    def __init__(self):
        self.log: List[Diagnosis] = []

    def scan(
        self,
        t: int,
        sub_metrics: Dict,
        macro: MacroWorld,
        cohorts: Dict[str, Cohort],
        pressure: Dict[str, float],
    ) -> Diagnosis:
        asis = [macro.asi.calculate(s) for s in macro.systems.values()]
        warns = []

        if sub_metrics["alive"] < 5:
            warns.append("底层崩溃风险")
        if sub_metrics["gini"] > 0.6:
            warns.append("资源极端不平等")
        if pressure["mobilization"] > 0.15:
            warns.append("中观动员压力升高")
        if max(asis) >= 85:
            warns.append("宏观主体化突破")
        if any(s.stability < 40 for s in macro.systems.values()):
            warns.append("系统稳定性预警")

        d = Diagnosis(
            time=t,
            substrate_alive=sub_metrics["alive"],
            macro_mean_asi=round(sum(asis) / len(asis), 2),
            macro_max_asi=round(max(asis), 2),
            meso_mobilization=pressure["mobilization"],
            meso_gini=sub_metrics["gini"],
            warnings=warns,
        )
        self.log.append(d)
        return d


# ═════════════════════════════════════════════════════════
# §6  UNIFIED ENGINE
# ═════════════════════════════════════════════════════════

class JAEUnified:
    """跨尺度统一引擎

    主循环每步执行：
        L0 (Substrate)  →  跑 N 个 agent step
        L1 (Meso)       →  聚合 cohort + 计算压力
        L2 (Macro)      →  五系统演化 + 接收中观压力
        L2 → L0         →  宏观 stress 反过来改变 share/attack 奖励偏置
        Meta            →  诊断
    """

    def __init__(
        self,
        n_agents: int = 30,
        w: int = 24,
        h: int = 24,
        seed: int = 2026,
        substrate_steps_per_macro: int = 5,
    ):
        self.sub = SubstrateWorld(n_agents, w, h, seed)
        self.learners = {i: SubstrateLearner(seed + i)
                         for i in range(n_agents)}
        self.macro = MacroWorld()
        self.meso = MesoAggregator()
        self.observer = Observer()
        self.substrate_steps_per_macro = substrate_steps_per_macro
        self.sub_metrics: Dict = {}
        self.cohorts: Dict[str, Cohort] = {}
        self.pressure: Dict[str, float] = {"mobilization": 0.0, "cohesion": 0.5}

    # -------------------------------------------------
    # LAYER 0
    # -------------------------------------------------

    def _step_substrate(self) -> None:
        ids = [i for i, a in self.sub.agents.items() if a.alive]
        self.sub.rng.shuffle(ids)
        for i in ids:
            s = self.sub.state(self.sub.obs(i))
            a = self.learners[i].act(s)
            r, no = self.sub.act(i, a)
            ns = self.sub.state(no)
            self.learners[i].update(s, a, r, ns)
            self.learners[i].decay()
        self.sub.tick()

    # -------------------------------------------------
    # LAYER 2 → LAYER 0  (宏观压力反馈到微观奖励)
    # -------------------------------------------------

    def _macro_to_substrate(self) -> None:
        avg_stress = sum(s.stress for s in self.macro.systems.values()) / 5.0
        # 高压环境下：分享奖励下降，攻击成本下降
        self.sub.reward_bias["share"] = 2.0 * (1.0 - avg_stress / 150.0)
        self.sub.reward_bias["attack"] = -1.5 + (avg_stress / 100.0) * 2.0

    # -------------------------------------------------
    # MAIN STEP
    # -------------------------------------------------

    def step(self) -> Diagnosis:
        # L0
        for _ in range(self.substrate_steps_per_macro):
            self._step_substrate()
        self.sub_metrics = self.sub.metrics(window=30)

        # L1
        self.cohorts = self.meso.aggregate(self.sub)
        self.pressure = self.meso.coupling_pressure(self.cohorts)

        # L2
        self.macro.step(meso_pressure=self.pressure)

        # L2 → L0
        self._macro_to_substrate()

        # Meta
        return self.observer.scan(
            t=self.macro.time,
            sub_metrics=self.sub_metrics,
            macro=self.macro,
            cohorts=self.cohorts,
            pressure=self.pressure,
        )

    def run(self, steps: int = 60, verbose_every: int = 10) -> List[Diagnosis]:
        out = []
        for _ in range(steps):
            d = self.step()
            out.append(d)
            if verbose_every and d.time % verbose_every == 0:
                self._print_line(d)
        return out

    def _print_line(self, d: Diagnosis) -> None:
        warn = " | ".join(d.warnings) if d.warnings else "-"
        print(
            f"t={d.time:>3}  alive={d.substrate_alive:>2}  "
            f"ASI_mean={d.macro_mean_asi:>6.2f}  "
            f"ASI_max={d.macro_max_asi:>6.2f}  "
            f"mob={d.meso_mobilization:.3f}  "
            f"gini={d.meso_gini:.3f}  {warn}"
        )

    # -------------------------------------------------
    # REPORT
    # -------------------------------------------------

    def report(self) -> None:
        print("\n" + "=" * 78)
        print("JAE UNIFIED WORLD MODEL v7.0 — FINAL REPORT")
        print("=" * 78)

        print(f"\n[Layer 0 · Substrate]  t={self.sub.t}")
        print(f"  alive          : {self.sub_metrics.get('alive', 0)}")
        print(f"  cooperation    : {self.sub_metrics.get('cooperation_rate', 0):.3f}")
        print(f"  conflict       : {self.sub_metrics.get('conflict_rate', 0):.3f}")
        print(f"  gini           : {self.sub_metrics.get('gini', 0):.3f}")
        print(f"  avg_trust      : {self.sub_metrics.get('avg_trust', 0):.3f}")
        print(f"  state_entropy  : {self.sub_metrics.get('state_entropy', 0):.3f}")

        print("\n[Layer 1 · Meso]  cohorts")
        for name, c in self.cohorts.items():
            print(f"  {name:<7} size={c.size:<3} cap={c.capacity:.2f} "
                  f"coh={c.cohesion:.3f} griev={c.grievance:.3f} "
                  f"mob={c.mobilization:.3f}")

        print("\n[Layer 2 · Macro]  systems")
        for item in self.macro.asi.rank(self.macro.systems):
            st = self.macro.systems[
                next(k for k in self.macro.systems
                     if k.value == item["system"])
            ]
            phase = determine_ai_phase(item["ASI"])
            print(f"  {item['system']:<8} ASI={item['ASI']:>6.2f} "
                  f"zone={item['zone']:<8} phase={phase.value:<9} "
                  f"stab={st.stability:>5.1f} stress={st.stress:>5.1f} "
                  f"res={st.resources:>5.1f} dep={st.dependency:>4.1f}")

        print("\n[Layer 3 · Meta]  latest diagnosis")
        if self.observer.log:
            d = self.observer.log[-1]
            print(f"  warnings: {d.warnings or 'none'}")
        print("=" * 78)

    # -------------------------------------------------
    # EXPORT
    # -------------------------------------------------

    def export(self, path: str = "jae_v7_metrics.csv") -> None:
        if not self.observer.log:
            print("[JAE] No data to export")
            return
        fields = list(asdict(self.observer.log[0]).keys())
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for d in self.observer.log:
                row = asdict(d)
                row["warnings"] = ";".join(row["warnings"])
                w.writerow(row)
        print(f"[JAE] metrics exported: {path}")

    def save(self, path: str = "jae_v7_state.json") -> None:
        data = {
            "version": "JAE Unified v7.0",
            "substrate": self.sub_metrics,
            "cohorts": {k: asdict(v) for k, v in self.cohorts.items()},
            "macro": {
                k.value: v.as_dict() for k, v in self.macro.systems.items()
            },
            "observer": [asdict(d) for d in self.observer.log[-100:]],
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[JAE] state saved: {path}")


# ═════════════════════════════════════════════════════════
# §7  实验入口
# ═════════════════════════════════════════════════════════

def scenario_no_shaping() -> JAEUnified:
    """实验 B：关闭 share/attack 的奖励塑造 —— 检验合作是否真的涌现"""
    j = JAEUnified()
    j.sub.reward_bias["share"] = 0.0
    j.sub.reward_bias["attack"] = 0.0
    # 同时禁用宏观→微观反馈，避免覆盖
    j._macro_to_substrate = lambda: None  # type: ignore
    return j


def scenario_scarcity() -> JAEUnified:
    """实验 C：资源稀缺 —— 观察不平等与冲突"""
    j = JAEUnified()
    for p in j.sub.resources:
        j.sub.resources[p] *= 0.3
    return j


def main():
    print("\n" + "█" * 78)
    print("JAE UNIFIED v7.0 — Boot Sequence")
    print("█" * 78)

    # ---- A：默认系统 ----
    print("\n[A] 默认参数 60 步")
    jA = JAEUnified(seed=2026)
    jA.run(steps=60, verbose_every=10)
    jA.report()
    jA.export("jae_v7_A_default.csv")
    jA.save("jae_v7_A_state.json")

    # ---- B：关闭奖励塑造 ----
    print("\n[B] 关闭 share/attack 奖励塑造 60 步")
    jB = scenario_no_shaping()
    jB.run(steps=60, verbose_every=10)
    jB.export("jae_v7_B_noshaping.csv")

    # ---- C：资源稀缺 ----
    print("\n[C] 资源稀缺 60 步")
    jC = scenario_scarcity()
    jC.run(steps=60, verbose_every=10)
    jC.export("jae_v7_C_scarcity.csv")

    # ---- 对照 ----
    print("\n" + "=" * 78)
    print("对照汇总")
    print("=" * 78)
    for tag, j in [("A 默认", jA), ("B 无塑造", jB), ("C 稀缺", jC)]:
        m = j.sub.metrics(window=100)
        print(f"  {tag:<10} "
              f"alive={m['alive']:>2}  "
              f"coop={m['cooperation_rate']:.3f}  "
              f"conflict={m['conflict_rate']:.3f}  "
              f"gini={m['gini']:.3f}  "
              f"trust={m['avg_trust']:.3f}")

    print("\n[JAE] All outputs written. Done.")


if __name__ == "__main__":
    main()