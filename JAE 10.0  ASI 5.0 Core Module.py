"""
============================================================
JAE 10.0 — ASI 5.0 CORE RUNTIME
============================================================

Five-system AI Civilization / World-State model

Systems:
    finance
    energy
    supply_chain
    military
    information

ASI 5.0 dimensions:
    autonomy
    recursive_improvement
    goal_formation
    resource_access
    cross_system_influence
    decision_irreversibility
    execution_capability

Outputs:
    1. ASI 5.0 score for each system
    2. Cross-system coupling matrix
    3. Ranked feedback loops
    4. World Stability Index
    5. 30-day risk variables
    6. 90-day risk variables
    7. Overall JAE risk state

This is a research/simulation model, not an official
statistical index or investment recommendation.
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from copy import deepcopy
import json
import math
from datetime import datetime, timezone


# ============================================================
# 1. SYSTEM DEFINITIONS
# ============================================================

SYSTEMS = [
    "finance",
    "energy",
    "supply_chain",
    "military",
    "information",
]


ASI_DIMENSIONS = [
    "autonomy",
    "recursive_improvement",
    "goal_formation",
    "resource_access",
    "cross_system_influence",
    "decision_irreversibility",
    "execution_capability",
]


# ============================================================
# 2. ASI 5.0 WEIGHTS
# ============================================================

ASI_WEIGHTS = {
    "autonomy": 0.20,
    "recursive_improvement": 0.15,
    "goal_formation": 0.10,
    "resource_access": 0.15,
    "cross_system_influence": 0.15,
    "decision_irreversibility": 0.15,
    "execution_capability": 0.10,
}


# ============================================================
# 3. CROSS-SYSTEM COUPLING MATRIX
# ============================================================

COUPLING_MATRIX = {
    ("energy", "supply_chain"): 0.91,
    ("finance", "energy"): 0.88,
    ("information", "finance"): 0.87,
    ("military", "information"): 0.86,
    ("information", "energy"): 0.84,
    ("supply_chain", "finance"): 0.82,
    ("military", "energy"): 0.81,
    ("military", "supply_chain"): 0.79,
}


# ============================================================
# 4. FEEDBACK LOOPS
# ============================================================

FEEDBACK_LOOPS = {
    "energy_inflation_rates": {
        "name": "Energy → Inflation → Long Rates → Finance",
        "nodes": [
            "energy",
            "inflation",
            "long_rates",
            "finance",
        ],
        "base_gain": 0.92,
        "irreversibility": 0.78,
    },

    "ai_power_capital": {
        "name": "AI → Power → Capital → Rates → AI",
        "nodes": [
            "ai",
            "power",
            "capital",
            "long_rates",
            "ai",
        ],
        "base_gain": 0.89,
        "irreversibility": 0.74,
    },

    "geopolitics_energy_fiscal": {
        "name": "Geopolitics → Energy → Fiscal → Bonds",
        "nodes": [
            "military",
            "energy",
            "fiscal",
            "bonds",
            "finance",
        ],
        "base_gain": 0.87,
        "irreversibility": 0.86,
    },

    "ai_information_finance": {
        "name": "AI → Information → Finance → Capital → AI",
        "nodes": [
            "ai",
            "information",
            "finance",
            "capital",
            "ai",
        ],
        "base_gain": 0.81,
        "irreversibility": 0.69,
    },
}


# ============================================================
# 5. WORLD STATE
# ============================================================

@dataclass
class SystemState:
    name: str
    indicators: Dict[str, float]
    asi_score: float = 0.0


@dataclass
class WorldState:
    systems: Dict[str, SystemState]
    macro: Dict[str, float]

    stability: float = 0.0

    events: List[str] = field(default_factory=list)


# ============================================================
# 6. ASI ENGINE
# ============================================================

class ASI5Engine:

    def validate(self, indicators: Dict[str, float]) -> None:
        missing = [
            x for x in ASI_DIMENSIONS
            if x not in indicators
        ]

        if missing:
            raise ValueError(
                f"Missing ASI dimensions: {missing}"
            )

        for key in ASI_DIMENSIONS:
            value = indicators[key]

            if not 0 <= value <= 100:
                raise ValueError(
                    f"{key} must be between 0 and 100"
                )

    def score(
        self,
        indicators: Dict[str, float],
    ) -> float:

        self.validate(indicators)

        score = 0.0

        for dimension, weight in ASI_WEIGHTS.items():
            score += (
                indicators[dimension] * weight
            )

        return round(
            min(100.0, max(0.0, score)),
            2,
        )

    def evaluate(
        self,
        world: WorldState,
    ) -> Dict[str, float]:

        scores = {}

        for system in SYSTEMS:

            state = world.systems[system]

            state.asi_score = self.score(
                state.indicators
            )

            scores[system] = state.asi_score

        return scores


# ============================================================
# 7. COUPLING ENGINE
# ============================================================

class CouplingEngine:

    def pressure(
        self,
        asi_scores: Dict[str, float],
    ) -> float:

        numerator = 0.0
        denominator = 0.0

        for (a, b), coupling in COUPLING_MATRIX.items():

            a_score = asi_scores.get(a, 0)
            b_score = asi_scores.get(b, 0)

            system_pressure = (
                (a_score + b_score) / 200.0
            )

            numerator += (
                system_pressure * coupling
            )

            denominator += coupling

        if denominator == 0:
            return 0.0

        return round(
            100 * numerator / denominator,
            2,
        )

    def ranked_pairs(self) -> List[Dict]:

        result = []

        for (a, b), score in COUPLING_MATRIX.items():

            result.append({
                "from": a,
                "to": b,
                "coupling": round(
                    score * 100,
                    2,
                ),
            })

        return sorted(
            result,
            key=lambda x: x["coupling"],
            reverse=True,
        )


# ============================================================
# 8. FEEDBACK LOOP ENGINE
# ============================================================

class FeedbackEngine:

    def rank(
        self,
        world: WorldState,
        asi_scores: Dict[str, float],
    ) -> List[Dict]:

        macro = world.macro

        oil = macro.get(
            "oil_price",
            90,
        )

        rate_stress = macro.get(
            "long_rate_stress",
            50,
        )

        geopolitical = macro.get(
            "geopolitical_stress",
            50,
        )

        ai_score = asi_scores.get(
            "information",
            0,
        )

        results = []

        for key, loop in FEEDBACK_LOOPS.items():

            score = (
                loop["base_gain"] * 100
            )

            multiplier = 1.0

            # Energy stress
            if oil >= 100:
                multiplier += 0.05

            if oil >= 120:
                multiplier += 0.08

            # Long-duration financing stress
            if rate_stress >= 60:
                multiplier += 0.05

            if rate_stress >= 75:
                multiplier += 0.08

            # Geopolitical stress
            if geopolitical >= 60:
                multiplier += 0.05

            if geopolitical >= 75:
                multiplier += 0.08

            # Information / AI acceleration
            if ai_score >= 80:
                multiplier += 0.03

            risk_score = min(
                100.0,
                score * multiplier,
            )

            results.append({
                "id": key,
                "name": loop["name"],
                "risk_score": round(
                    risk_score,
                    2,
                ),
                "base_gain": loop["base_gain"],
                "irreversibility": loop[
                    "irreversibility"
                ],
                "nodes": loop["nodes"],
            })

        return sorted(
            results,
            key=lambda x: x["risk_score"],
            reverse=True,
        )


# ============================================================
# 9. STABILITY ENGINE
# ============================================================

class StabilityEngine:

    def calculate(
        self,
        asi_scores: Dict[str, float],
        coupling_pressure: float,
        feedback_risk: float,
        macro: Dict[str, float],
    ) -> float:

        mean_asi = (
            sum(asi_scores.values())
            / len(asi_scores)
        )

        oil = macro.get(
            "oil_price",
            90,
        )

        rate_stress = macro.get(
            "long_rate_stress",
            50,
        )

        geopolitical = macro.get(
            "geopolitical_stress",
            50,
        )

        energy_stress = min(
            100,
            max(
                0,
                (oil - 70) * 1.5,
            ),
        )

        # Higher risk => lower stability.
        stability = (
            100

            - 0.18 * mean_asi

            - 0.25 * coupling_pressure

            - 0.25 * feedback_risk

            - 0.15 * energy_stress

            - 0.10 * rate_stress

            - 0.07 * geopolitical
        )

        return round(
            max(
                0,
                min(
                    100,
                    stability,
                ),
            ),
            2,
        )

    @staticmethod
    def regime(
        stability: float,
    ) -> str:

        if stability >= 70:
            return "STABLE"

        if stability >= 60:
            return "WATCH"

        if stability >= 50:
            return "HIGH_PRESSURE"

        if stability >= 35:
            return "SYSTEMIC_RISK"

        return "CRITICAL"


# ============================================================
# 10. RISK VARIABLE ENGINE
# ============================================================

class RiskVariableEngine:

    VARIABLES = [
        "oil_price",
        "long_rate_stress",
        "geopolitical_stress",
        "ai_capex_stress",
        "shipping_stress",
        "refining_stress",
        "power_grid_stress",
        "supply_chain_stress",
        "financial_stress",
        "information_volatility",
    ]

    def evaluate_30d(
        self,
        macro: Dict[str, float],
    ) -> Dict[str, float]:

        return {
            "oil_price": macro.get(
                "oil_price",
                90,
            ),

            "long_rate_stress": macro.get(
                "long_rate_stress",
                50,
            ),

            "geopolitical_stress": macro.get(
                "geopolitical_stress",
                50,
            ),

            "ai_capex_stress": macro.get(
                "ai_capex_stress",
                45,
            ),

            "shipping_stress": macro.get(
                "shipping_stress",
                55,
            ),

            "refining_stress": macro.get(
                "refining_stress",
                60,
            ),

            "power_grid_stress": macro.get(
                "power_grid_stress",
                55,
            ),

            "supply_chain_stress": macro.get(
                "supply_chain_stress",
                55,
            ),

            "financial_stress": macro.get(
                "financial_stress",
                55,
            ),

            "information_volatility": macro.get(
                "information_volatility",
                65,
            ),
        }

    def evaluate_90d(
        self,
        macro: Dict[str, float],
    ) -> Dict[str, float]:

        result = self.evaluate_30d(macro)

        # Structural risk drift.
        drift = {
            "oil_price": 3,
            "long_rate_stress": 5,
            "geopolitical_stress": 4,
            "ai_capex_stress": 4,
            "shipping_stress": 5,
            "refining_stress": 5,
            "power_grid_stress": 6,
            "supply_chain_stress": 4,
            "financial_stress": 5,
            "information_volatility": 3,
        }

        for key, delta in drift.items():

            result[key] = min(
                100,
                result[key] + delta,
            )

        return result


# ============================================================
# 11. SCENARIO ENGINE
# ============================================================

class ScenarioEngine:

    def project(
        self,
        world: WorldState,
        days: int,
    ) -> Dict:

        macro = deepcopy(
            world.macro
        )

        if days == 30:

            macro["oil_price"] += 2
            macro["long_rate_stress"] += 2
            macro["geopolitical_stress"] += 1

        elif days == 90:

            macro["oil_price"] += 4
            macro["long_rate_stress"] += 5
            macro["geopolitical_stress"] += 4

        else:

            raise ValueError(
                "Only 30 or 90 day scenarios supported."
            )

        return macro


# ============================================================
# 12. JAE 10.0 CORE RUNTIME
# ============================================================

class JAEC10Runtime:

    VERSION = "10.0"
    ASI_VERSION = "5.0"

    def __init__(self):

        self.asi_engine = ASI5Engine()

        self.coupling_engine = (
            CouplingEngine()
        )

        self.feedback_engine = (
            FeedbackEngine()
        )

        self.stability_engine = (
            StabilityEngine()
        )

        self.risk_engine = (
            RiskVariableEngine()
        )

        self.scenario_engine = (
            ScenarioEngine()
        )

    def run(
        self,
        world: WorldState,
    ) -> Dict:

        # ----------------------------------------------------
        # Step 1: ASI
        # ----------------------------------------------------

        asi_scores = (
            self.asi_engine.evaluate(
                world
            )
        )

        # ----------------------------------------------------
        # Step 2: Coupling
        # ----------------------------------------------------

        coupling_pressure = (
            self.coupling_engine.pressure(
                asi_scores
            )
        )

        # ----------------------------------------------------
        # Step 3: Feedback loops
        # ----------------------------------------------------

        loops = (
            self.feedback_engine.rank(
                world,
                asi_scores,
            )
        )

        top_loop_risk = (
            loops[0]["risk_score"]
            if loops
            else 0
        )

        # ----------------------------------------------------
        # Step 4: Stability
        # ----------------------------------------------------

        stability = (
            self.stability_engine.calculate(
                asi_scores,
                coupling_pressure,
                top_loop_risk,
                world.macro,
            )
        )

        world.stability = stability

        # ----------------------------------------------------
        # Step 5: Risk variables
        # ----------------------------------------------------

        risk_30 = (
            self.risk_engine.evaluate_30d(
                world.macro
            )
        )

        risk_90 = (
            self.risk_engine.evaluate_90d(
                world.macro
            )
        )

        # ----------------------------------------------------
        # Step 6: Result
        # ----------------------------------------------------

        return {
            "jae_version":
                self.VERSION,

            "asi_version":
                self.ASI_VERSION,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "asi_scores":
                asi_scores,

            "coupling_pressure":
                coupling_pressure,

            "coupling_matrix":
                self.coupling_engine.ranked_pairs(),

            "feedback_loops":
                loops,

            "world_stability":
                stability,

            "stability_regime":
                self.stability_engine.regime(
                    stability
                ),

            "risk_30d":
                risk_30,

            "risk_90d":
                risk_90,

            "macro":
                world.macro,

            "events":
                world.events,
        }


# ============================================================
# 13. DEFAULT WORLD
# ============================================================

def create_default_world() -> WorldState:

    common = {
        "autonomy": 75,
        "recursive_improvement": 70,
        "goal_formation": 62,
        "resource_access": 68,
        "cross_system_influence": 72,
        "decision_irreversibility": 70,
        "execution_capability": 65,
    }

    indicators = {

        "finance": {
            **common,
            "autonomy": 78,
            "resource_access": 82,
            "execution_capability": 76,
        },

        "energy": {
            **common,
            "autonomy": 62,
            "resource_access": 70,
        },

        "supply_chain": {
            **common,
            "autonomy": 71,
            "cross_system_influence": 78,
        },

        "military": {
            **common,
            "decision_irreversibility": 82,
            "execution_capability": 72,
        },

        "information": {
            **common,
            "autonomy": 88,
            "recursive_improvement": 82,
            "execution_capability": 84,
        },
    }

    systems = {
        system:
        SystemState(
            name=system,
            indicators=indicators[system],
        )

        for system in SYSTEMS
    }

    macro = {

        # Current-model input.
        "oil_price": 101.0,

        # Normalized stress: 0-100.
        "long_rate_stress": 62.0,

        "geopolitical_stress": 68.0,

        "ai_capex_stress": 45.0,

        "shipping_stress": 65.0,

        "refining_stress": 63.0,

        "power_grid_stress": 60.0,

        "supply_chain_stress": 58.0,

        "financial_stress": 58.0,

        "information_volatility": 70.0,
    }

    return WorldState(
        systems=systems,
        macro=macro,
        events=[
            "energy logistics stress",
            "elevated long-duration financing pressure",
            "AI infrastructure expansion",
            "cross-system geopolitical coupling",
        ],
    )


# ============================================================
# 14. CLI
# ============================================================

def main():

    world = create_default_world()

    runtime = JAEC10Runtime()

    result = runtime.run(
        world
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()