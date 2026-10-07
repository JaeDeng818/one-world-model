"""
JAE 20.0 + ASI 10.0
World–AI–Civilization Co-Evolution Engine
Single-file runnable research core.

Run:
    pip install numpy
    python jae_20_0_asi_10_0.py
"""

from dataclasses import dataclass, asdict
from typing import Dict, Optional
import json
import numpy as np


# =========================
# Configuration
# =========================

@dataclass
class Config:
    jae_version: str = "20.0"
    asi_version: str = "10.0"
    seed: int = 20261007
    days: int = 90

    # World system weights:
    # financial, energy, supply_chain, trade, geopolitics, technology_ai
    world_weights: tuple = (0.18, 0.14, 0.14, 0.14, 0.18, 0.22)

    # ASI 10.0 weights:
    # autonomy, recursive, coupling, decision, irreversibility, scale,
    # learning, model_building, adaptation, persistence, feedback
    asi_weights: tuple = (
        0.10, 0.12, 0.12, 0.12, 0.09, 0.07,
        0.09, 0.09, 0.07, 0.06, 0.07
    )

    asi_nonlinear_coupling: float = 0.08
    asi_nonlinear_feedback: float = 0.06

    normal_shock_probability: float = 0.95
    normal_shock_scale: float = 1.0
    tail_shock_scale: float = 4.0

    collapse_stability: float = 20.0
    transition_ctp: float = 0.50
    critical_ctp: float = 0.75


# =========================
# State
# =========================

@dataclass
class World:
    financial: float = 35.0
    energy: float = 30.0
    supply_chain: float = 30.0
    trade: float = 28.0
    geopolitics: float = 35.0
    technology_ai: float = 25.0
    liquidity: float = 65.0
    coupling: float = 35.0
    stress: float = 0.0
    velocity: float = 0.0
    acceleration: float = 0.0
    stability: float = 70.0


@dataclass
class AI:
    autonomy: float = 25.0
    recursive_autonomy: float = 20.0
    cross_system_coupling: float = 20.0
    decision_power: float = 20.0
    irreversibility: float = 15.0
    scale: float = 25.0
    learning_velocity: float = 30.0
    model_building: float = 25.0
    adaptation: float = 25.0
    objective_persistence: float = 20.0
    feedback_amplification: float = 20.0
    resource_access: float = 25.0
    compute: float = 30.0
    asi: float = 0.0
    subjectivity: float = 0.0
    evolution_rate: float = 0.0


@dataclass
class Civilization:
    economy: float = 65.0
    technology: float = 55.0
    governance: float = 60.0
    resource_security: float = 65.0
    social_stability: float = 65.0
    stability: float = 65.0
    phase: str = "digital"


@dataclass
class Observer:
    observation_quality: float = 70.0
    model_accuracy: float = 65.0
    reflexivity: float = 20.0
    model_world_influence: float = 10.0


@dataclass
class Risk:
    systemic: float = 0.0
    ai_systemic: float = 0.0
    ctp: float = 0.0
    world_reflexivity: float = 0.0
    civilization_transition: float = 0.0
    regime: str = "stable"


@dataclass
class State:
    world: World
    ai: AI
    civilization: Civilization
    observer: Observer
    risk: Risk
    day: int = 0


# =========================
# Utilities
# =========================

def clip(x, lo=0.0, hi=100.0):
    return float(np.clip(x, lo, hi))


def sigmoid(x):
    x = np.clip(x, -60, 60)
    return 1.0 / (1.0 + np.exp(-x))


def new_state() -> State:
    return State(World(), AI(), Civilization(), Observer(), Risk())


def world_stress(w: World, cfg: Config) -> float:
    x = np.array([
        w.financial, w.energy, w.supply_chain,
        w.trade, w.geopolitics, w.technology_ai
    ])
    return float(np.dot(x, np.array(cfg.world_weights)))


# =========================
# ASI 10.0
# =========================

def calculate_asi(ai: AI, cfg: Config) -> float:
    x = np.array([
        ai.autonomy,
        ai.recursive_autonomy,
        ai.cross_system_coupling,
        ai.decision_power,
        ai.irreversibility,
        ai.scale,
        ai.learning_velocity,
        ai.model_building,
        ai.adaptation,
        ai.objective_persistence,
        ai.feedback_amplification,
    ])
    base = float(np.dot(x, np.array(cfg.asi_weights)))
    nonlinear = (
        cfg.asi_nonlinear_coupling
        * ai.cross_system_coupling
        * ai.recursive_autonomy / 100.0
        + cfg.asi_nonlinear_feedback
        * ai.feedback_amplification
        * ai.irreversibility / 100.0
    )
    return clip(base + nonlinear)


def update_asi(state: State, cfg: Config):
    old = state.ai.asi
    state.ai.asi = calculate_asi(state.ai, cfg)
    state.ai.subjectivity = clip(
        0.22 * state.ai.autonomy
        + 0.18 * state.ai.objective_persistence
        + 0.16 * state.ai.adaptation
        + 0.16 * state.ai.resource_access
        + 0.14 * state.ai.decision_power
        + 0.14 * state.ai.feedback_amplification
    )
    state.ai.evolution_rate = state.ai.asi - old


# =========================
# World Engine
# =========================

def shocks(rng, cfg: Config):
    tail = rng.random() > cfg.normal_shock_probability
    scale = cfg.tail_shock_scale if tail else cfg.normal_shock_scale
    return rng.normal(0, scale, 6)


def evolve_world(state: State, rng, cfg: Config):
    w, ai, c = state.world, state.ai, state.civilization
    old = w.stress
    s = shocks(rng, cfg)

    w.financial += s[0] + .020*w.geopolitics + .015*w.energy - .020*w.liquidity
    w.energy += s[1] + .025*w.geopolitics + .012*ai.scale
    w.supply_chain += s[2] + .025*w.energy + .020*w.geopolitics
    w.trade += s[3] + .020*w.financial + .020*w.supply_chain - .015*w.liquidity
    w.geopolitics += s[4] + .025*w.supply_chain + .015*w.energy
    w.technology_ai += s[5] + .020*ai.asi - .010*w.geopolitics

    w.liquidity += -.020*w.financial - .010*w.geopolitics + .030*c.governance

    values = np.array([
        w.financial, w.energy, w.supply_chain,
        w.trade, w.geopolitics, w.technology_ai
    ])
    sync = 100 - min(100, float(np.std(values))*3)
    w.coupling += .020*sync + .010*ai.cross_system_coupling

    for name in [
        "financial", "energy", "supply_chain",
        "trade", "geopolitics", "technology_ai"
    ]:
        setattr(w, name, clip(getattr(w, name) * .985))

    w.liquidity = clip(w.liquidity)
    w.coupling = clip(w.coupling)
    w.stress = world_stress(w, cfg)
    w.velocity = w.stress - old
    w.acceleration = w.velocity - getattr(w, "_last_velocity", 0.0)
    w._last_velocity = w.velocity

    w.stability = clip(
        100 - w.stress - .18*w.coupling + .20*w.liquidity
    )


# =========================
# AI Engine
# =========================

def evolve_ai(state: State, rng, cfg: Config):
    ai, w, c = state.ai, state.world, state.civilization
    old = ai.asi
    innovation = float(rng.normal(0, .8))

    ai.learning_velocity += .15*innovation + .030*ai.compute
    ai.model_building += .020*ai.learning_velocity + .015*ai.adaptation
    ai.adaptation += .018*ai.learning_velocity + .010*w.stress
    ai.autonomy += .018*ai.learning_velocity + .010*ai.resource_access/100
    ai.recursive_autonomy += .012*ai.autonomy + .010*ai.model_building
    ai.cross_system_coupling += .020*ai.autonomy + .010*ai.decision_power
    ai.decision_power += .015*ai.cross_system_coupling + .008*ai.model_building
    ai.irreversibility += .010*ai.decision_power + .008*ai.feedback_amplification
    ai.objective_persistence += .010*ai.autonomy + .010*ai.model_building
    ai.feedback_amplification += .012*ai.cross_system_coupling + .010*ai.recursive_autonomy
    ai.scale += .010*ai.resource_access + .008*ai.compute

    ai.resource_access += .020*ai.model_building + .015*ai.learning_velocity
    ai.compute += .020*ai.resource_access - .012*w.energy

    for name in [
        "autonomy", "recursive_autonomy", "cross_system_coupling",
        "decision_power", "irreversibility", "scale",
        "learning_velocity", "model_building", "adaptation",
        "objective_persistence", "feedback_amplification",
        "resource_access", "compute"
    ]:
        setattr(ai, name, clip(getattr(ai, name)))

    update_asi(state, cfg)
    ai.evolution_rate = ai.asi - old


# =========================
# Civilization Engine
# =========================

def evolve_civilization(state: State):
    c, w, ai = state.civilization, state.world, state.ai

    productivity = .25*ai.model_building + .20*ai.learning_velocity + .15*ai.decision_power

    c.economy += .030*productivity - .010*w.energy - .015*w.financial
    c.technology += .025*ai.learning_velocity + .020*ai.model_building
    c.governance += .025*(100-c.governance) - .012*ai.irreversibility
    c.resource_security += .010*c.economy - .025*w.energy - .020*w.supply_chain

    conflict = .25*w.geopolitics + .20*w.financial + .15*w.supply_chain
    c.social_stability += .015*c.governance - .006*conflict - .012*ai.irreversibility

    for name in ["economy", "technology", "governance",
                 "resource_security", "social_stability"]:
        setattr(c, name, clip(getattr(c, name)))

    c.stability = clip(
        .22*c.economy + .20*c.technology + .22*c.governance
        + .18*c.resource_security + .18*c.social_stability
        - .15*w.stress - .10*ai.irreversibility
    )

    if c.stability >= 70:
        c.phase = "adaptive"
    elif c.stability >= 50:
        c.phase = "digital"
    elif c.stability >= 35:
        c.phase = "transition"
    elif c.stability >= 20:
        c.phase = "critical"
    else:
        c.phase = "collapse-like"


# =========================
# Observer + Risk
# =========================

def update_observer(state: State):
    o, w, ai = state.observer, state.world, state.ai
    signal = 100 - min(100, abs(w.acceleration)*10)
    o.observation_quality = clip(.98*o.observation_quality + .02*signal)
    o.model_accuracy = clip(.97*o.model_accuracy + .03*o.observation_quality)
    o.reflexivity = clip(o.reflexivity + .015*w.stress)
    o.model_world_influence = clip(
        .50*o.model_world_influence
        + .50*(o.reflexivity*ai.decision_power/100)
    )


def calculate_risk(state: State, cfg: Config):
    w, ai, c, o, r = state.world, state.ai, state.civilization, state.observer, state.risk

    r.systemic = clip(
        .35*w.stress + .18*abs(w.velocity) + .12*abs(w.acceleration)
        + .15*w.coupling + .10*ai.asi + .10*ai.irreversibility
    )

    r.ai_systemic = clip(
        .18*ai.autonomy + .20*ai.recursive_autonomy
        + .20*ai.cross_system_coupling + .16*ai.decision_power
        + .14*ai.irreversibility + .12*ai.feedback_amplification
    )

    transition_signal = (
        .40*r.systemic + .25*r.ai_systemic
        + .20*(100-c.stability) + .15*o.model_world_influence
    )
    r.ctp = float(sigmoid((transition_signal-50)/10))
    r.world_reflexivity = clip(.60*o.reflexivity + .40*o.model_world_influence)

    r.civilization_transition = clip(
        .25*ai.asi + .20*ai.subjectivity
        + .20*ai.cross_system_coupling + .15*c.technology
        + .20*(100-c.governance)
    )

    if c.stability < cfg.collapse_stability or r.ctp >= cfg.critical_ctp:
        r.regime = "critical"
    elif r.ctp >= cfg.transition_ctp:
        r.regime = "transition"
    elif c.stability < 50:
        r.regime = "fragile"
    else:
        r.regime = "stable"


# =========================
# Runtime
# =========================

def step(state: State, rng, cfg: Config):
    evolve_world(state, rng, cfg)
    evolve_ai(state, rng, cfg)
    evolve_civilization(state)
    update_observer(state)
    calculate_risk(state, cfg)
    state.day += 1
    return state


def run(days: int = 90, seed: int = 20261007) -> State:
    cfg = Config(days=days, seed=seed)
    rng = np.random.default_rng(seed)
    state = new_state()
    update_asi(state, cfg)
    calculate_risk(state, cfg)

    for _ in range(days):
        step(state, rng, cfg)

    return state


# =========================
# Counterfactual
# =========================

def clone_state(s: State) -> State:
    d = json.loads(json.dumps(asdict(s)))
    return State(
        World(**d["world"]),
        AI(**d["ai"]),
        Civilization(**d["civilization"]),
        Observer(**d["observer"]),
        Risk(**d["risk"]),
        d["day"],
    )


def counterfactual(
    baseline: State,
    interventions: Dict[str, float],
    days: int = 90,
    seed: int = 20261008,
):
    cfg = Config(days=days, seed=seed)
    a = clone_state(baseline)
    b = clone_state(baseline)

    for path, delta in interventions.items():
        target, field = path.split(".", 1)
        obj = getattr(b, target)
        setattr(obj, field, clip(getattr(obj, field) + delta))

    rng = np.random.default_rng(seed)
    for _ in range(days):
        step(a, rng, cfg)
        step(b, rng, cfg)

    return {
        "baseline": asdict(a),
        "counterfactual": asdict(b),
        "delta": {
            "world_stress": b.world.stress - a.world.stress,
            "asi": b.ai.asi - a.ai.asi,
            "civilization_stability": b.civilization.stability - a.civilization.stability,
            "systemic_risk": b.risk.systemic - a.risk.systemic,
            "ctp": b.risk.ctp - a.risk.ctp,
        }
    }


# =========================
# Vectorized Monte Carlo
# =========================

def monte_carlo(worlds=100_000, days=90, seed=20261007):
    """
    Vectorized multi-world experiment.
    Returns model-relative probability distributions.
    """

    cfg = Config(days=days, seed=seed)
    rng = np.random.default_rng(seed)

    # 20 variables per world.
    # 0..5 world systems
    # 6 coupling, 7 liquidity
    # 8..18 ASI dimensions
    # 19 civilization stability
    base = np.array([
        35,30,30,28,35,25,35,65,
        25,20,20,20,15,25,30,25,25,20,20,65
    ], dtype=np.float32)

    sd = np.array([
        5,5,5,4,6,5,5,5,
        4,4,5,4,4,5,4,4,4,4,4,6
    ], dtype=np.float32)

    x = rng.normal(base, sd, size=(worlds,20)).astype(np.float32)
    x = np.clip(x, 0, 100)

    previous_stress = np.zeros(worlds, dtype=np.float32)

    for _ in range(days):
        tail = rng.random(worlds) > cfg.normal_shock_probability
        scales = np.where(tail, cfg.tail_shock_scale, cfg.normal_shock_scale)

        shock = rng.normal(
            0, scales[:,None], size=(worlds,6)
        ).astype(np.float32)

        # World dynamics
        x[:,0] += shock[:,0] + .020*x[:,4] + .015*x[:,1] - .020*x[:,7]
        x[:,1] += shock[:,1] + .025*x[:,4] + .012*x[:,13]
        x[:,2] += shock[:,2] + .025*x[:,1] + .020*x[:,4]
        x[:,3] += shock[:,3] + .020*x[:,0] + .020*x[:,2] - .015*x[:,7]
        x[:,4] += shock[:,4] + .025*x[:,2] + .015*x[:,1]
        x[:,5] += shock[:,5] + .020*(.10*x[:,8]+.10*x[:,9]) - .010*x[:,4]

        x[:,7] += -.020*x[:,0] - .010*x[:,4] + .030*x[:,19]

        x[:,6] += .020*(100-np.std(x[:,:6],axis=1)*3) + .010*x[:,10]

        # AI dynamics
        innovation = rng.normal(0,.8,worlds)
        x[:,14] += .15*innovation + .030*x[:,13]
        x[:,15] += .020*x[:,14] + .015*x[:,16]
        x[:,16] += .018*x[:,14] + .010*(x[:,0]+x[:,4])/2
        x[:,8] += .018*x[:,14] + .010*x[:,15]
        x[:,9] += .012*x[:,8] + .010*x[:,15]
        x[:,10] += .020*x[:,8] + .010*x[:,11]
        x[:,11] += .015*x[:,10] + .008*x[:,15]
        x[:,12] += .010*x[:,11] + .008*x[:,18]
        x[:,17] += .010*x[:,8] + .010*x[:,15]
        x[:,18] += .012*x[:,10] + .010*x[:,9]
        x[:,13] += .010*x[:,17] + .008*x[:,13]
        x[:,13] += .010*x[:,17] - .005*x[:,1]

        # Civilization
        productivity = .25*x[:,15] + .20*x[:,14] + .15*x[:,11]
        x[:,19] += (
            .030*productivity - .010*x[:,1] - .015*x[:,0]
            + .015*x[:,19] - .012*x[:,12]
        )

        x[:,:6] *= .985
        x = np.clip(x,0,100)

        stress = np.dot(x[:,:6], np.array(cfg.world_weights,dtype=np.float32))
        velocity = stress - previous_stress
        previous_stress = stress

        asi = (
            .10*x[:,8]+.12*x[:,9]+.12*x[:,10]+.12*x[:,11]
            +.09*x[:,12]+.07*x[:,13]+.09*x[:,14]+.09*x[:,15]
            +.07*x[:,16]+.06*x[:,17]+.07*x[:,18]
            +cfg.asi_nonlinear_coupling*x[:,10]*x[:,9]/100
            +cfg.asi_nonlinear_feedback*x[:,18]*x[:,12]/100
        )
        asi = np.clip(asi,0,100)

        systemic = np.clip(
            .35*stress + .18*np.abs(velocity) + .15*x[:,6]
            + .10*asi + .10*x[:,12], 0, 100
        )

        ctp = 1/(1+np.exp(-(
            (.40*systemic + .25*asi + .20*(100-x[:,19]) - 50)/10
        )))

    stable = (x[:,19] >= 70) & (ctp < .25)
    fragile = (~stable) & (x[:,19] >= 50) & (ctp < .50)
    transition = (~stable) & (~fragile) & (ctp < .75)
    critical = (~stable) & (~fragile) & (~transition) & (x[:,19] >= 20)
    collapse = x[:,19] < 20

    return {
        "model": "JAE 20.0 + ASI 10.0",
        "worlds": int(worlds),
        "days": int(days),
        "seed": int(seed),
        "probabilities": {
            "stable": float(stable.mean()),
            "fragile": float(fragile.mean()),
            "transition": float(transition.mean()),
            "critical": float(critical.mean()),
            "collapse_like": float(collapse.mean()),
        },
        "statistics": {
            "mean_world_stress": float(stress.mean()),
            "p95_world_stress": float(np.percentile(stress,95)),
            "mean_asi": float(asi.mean()),
            "p95_asi": float(np.percentile(asi,95)),
            "mean_ctp": float(ctp.mean()),
            "p95_ctp": float(np.percentile(ctp,95)),
            "mean_civilization_stability": float(x[:,19].mean()),
            "p05_civilization_stability": float(np.percentile(x[:,19],5)),
        }
    }


# =========================
# Report / main
# =========================

def report(state: State):
    print("="*64)
    print("JAE 20.0 + ASI 10.0")
    print("WORLD–AI–CIVILIZATION CO-EVOLUTION ENGINE")
    print("="*64)
    print(f"Day                    : {state.day}")
    print(f"World Stress           : {state.world.stress:.2f}")
    print(f"World Stability        : {state.world.stability:.2f}")
    print(f"System Coupling        : {state.world.coupling:.2f}")
    print(f"Risk Velocity          : {state.world.velocity:.2f}")
    print(f"Risk Acceleration      : {state.world.acceleration:.2f}")
    print(f"ASI 10.0               : {state.ai.asi:.2f}")
    print(f"AI Subjectivity Index  : {state.ai.subjectivity:.2f}")
    print(f"AI Evolution Rate      : {state.ai.evolution_rate:.4f}")
    print(f"Civilization Stability : {state.civilization.stability:.2f}")
    print(f"Civilization Phase     : {state.civilization.phase}")
    print(f"Systemic Risk          : {state.risk.systemic:.2f}")
    print(f"AI Systemic Risk       : {state.risk.ai_systemic:.2f}")
    print(f"Critical Transition    : {state.risk.ctp:.4f}")
    print(f"World Reflexivity      : {state.risk.world_reflexivity:.2f}")
    print(f"Civilization CTI      : {state.risk.civilization_transition:.2f}")
    print(f"Regime                 : {state.risk.regime}")


def main():
    cfg = Config()

    state = run(cfg.days, cfg.seed)
    report(state)

    print("\n--- COUNTERFACTUAL: AI autonomy +10, coupling +10 ---")
    cf = counterfactual(
        state,
        {
            "ai.autonomy": 10,
            "ai.cross_system_coupling": 10,
        },
        days=90,
        seed=cfg.seed+1,
    )
    for k,v in cf["delta"].items():
        print(f"{k:24s}: {v:+.4f}")

    print("\n--- MONTE CARLO: 10,000 WORLDS DEMO ---")
    result = monte_carlo(10_000, 90, cfg.seed)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()