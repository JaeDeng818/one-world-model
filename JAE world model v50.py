from __future__ import annotations

from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple
import copy
import csv
import json
import math
import random
import time


# =========================================================
# JAE v50.0
# Universal World Intelligence System
# =========================================================

VERSION = "50.0.0"


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


# =========================================================
# 1. WORLD STATE
# =========================================================

@dataclass
class WorldState:

    timestamp: int

    variables: Dict[str, float] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: float = 0.0) -> float:

        return float(
            self.variables.get(key, default)
        )

    def set(self, key: str, value: float):

        self.variables[key] = float(value)


# =========================================================
# 2. KNOWLEDGE SYSTEM
# =========================================================

@dataclass
class KnowledgeItem:

    id: str

    claim: str

    source: str

    observed_at: float

    confidence: float = 0.5

    uncertainty: float = 0.5

    half_life_days: float = 30.0

    tags: List[str] = field(default_factory=list)

    supports: List[str] = field(default_factory=list)

    contradicts: List[str] = field(default_factory=list)

    def weight(
        self,
        now: Optional[float] = None
    ) -> float:

        now = now or time.time()

        age_days = max(
            0.0,
            (now - self.observed_at) / 86400.0
        )

        decay = math.exp(
            -math.log(2)
            * age_days
            / max(1e-6, self.half_life_days)
        )

        return clamp(
            self.confidence
            * (1.0 - self.uncertainty)
            * decay
        )


class KnowledgeGraph:

    def __init__(self):

        self.items: Dict[
            str,
            KnowledgeItem
        ] = {}

        self.edges = defaultdict(list)

    def add(
        self,
        item: KnowledgeItem
    ):

        self.items[item.id] = item

        for target in item.supports:

            self.edges[item.id].append(
                ("supports", target)
            )

        for target in item.contradicts:

            self.edges[item.id].append(
                ("contradicts", target)
            )

    def search(
        self,
        text: str
    ) -> List[KnowledgeItem]:

        terms = set(
            text.lower().split()
        )

        scored = []

        for item in self.items.values():

            content = (
                item.claim
                + " "
                + " ".join(item.tags)
            ).lower()

            score = len(
                terms.intersection(
                    set(content.split())
                )
            )

            if score:

                scored.append(
                    (
                        score * item.weight(),
                        item
                    )
                )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            x[1]
            for x in scored
        ]

    def conflict_pairs(self):

        conflicts = []

        for item in self.items.values():

            for other in item.contradicts:

                if other in self.items:

                    conflicts.append(
                        (item.id, other)
                    )

        return conflicts


# =========================================================
# 3. OBSERVATION
# =========================================================

@dataclass
class Observation:

    variable: str

    value: float

    reliability: float

    source: str

    noise: float

    timestamp: int


class ObservationEngine:

    def observe(
        self,
        world: WorldState,
        variable: str,
        accuracy: float = 0.85,
        source: str = "simulation",
        rng: Optional[random.Random] = None
    ) -> Observation:

        rng = rng or random.Random()

        true_value = world.get(
            variable
        )

        noise = rng.gauss(
            0.0,
            max(
                1e-5,
                (1.0 - accuracy) * 0.1
            )
        )

        value = true_value + noise

        reliability = clamp(
            accuracy - abs(noise)
        )

        return Observation(
            variable,
            value,
            reliability,
            source,
            noise,
            world.timestamp
        )


# =========================================================
# 4. BELIEF SYSTEM
# =========================================================

@dataclass
class Belief:

    variable: str

    estimate: float

    confidence: float = 0.5

    evidence_count: int = 0


class BeliefEngine:

    def update(
        self,
        old: Belief,
        observation: Observation
    ) -> Belief:

        alpha = clamp(
            observation.reliability
        )

        estimate = (
            old.estimate * (1.0 - alpha)
            + observation.value * alpha
        )

        confidence = clamp(
            old.confidence
            + 0.1 * observation.reliability
        )

        return Belief(
            variable=old.variable,
            estimate=estimate,
            confidence=confidence,
            evidence_count=old.evidence_count + 1
        )


# =========================================================
# 5. ANOMALY ENGINE
# =========================================================

@dataclass
class Anomaly:

    variable: str

    observed: float

    predicted: float

    magnitude: float

    persistence: float

    novelty: float

    model_conflict: float

    confidence: float = 0.5


class AnomalyDetector:

    def detect(
        self,
        variable,
        observed,
        predicted,
        persistence=0.0,
        novelty=0.0,
        model_conflict=0.0
    ):

        magnitude = clamp(
            abs(observed - predicted)
        )

        return Anomaly(
            variable,
            observed,
            predicted,
            magnitude,
            clamp(persistence),
            clamp(novelty),
            clamp(model_conflict)
        )

    def score(
        self,
        anomaly: Anomaly
    ):

        return clamp(
            0.35 * anomaly.magnitude
            + 0.20 * anomaly.persistence
            + 0.25 * anomaly.novelty
            + 0.20 * anomaly.model_conflict
        )


# =========================================================
# 6. EPISTEMIC RISK
# =========================================================

@dataclass
class KnowledgeGap:

    variable: str

    uncertainty: float

    importance: float

    decision_sensitivity: float

    observation_cost: float

    current_confidence: float


class VOIEngine:

    def calculate(
        self,
        gap: KnowledgeGap
    ):

        value = (
            gap.importance
            * gap.decision_sensitivity
            * gap.uncertainty
        )

        return max(
            0.0,
            value / (
                gap.observation_cost
                + 1e-6
            )
        )


class EpistemicRiskEngine:

    def calculate(
        self,
        uncertainty,
        sensitivity,
        impact
    ):

        return clamp(
            uncertainty
            * sensitivity
            * impact
        )


# =========================================================
# 7. RESEARCH / HYPOTHESIS
# =========================================================

@dataclass
class ResearchQuestion:

    id: str

    question: str

    target_variables: List[str]

    uncertainty: float

    decision_relevance: float

    novelty: float

    feasibility: float

    risk: float


@dataclass
class Hypothesis:

    id: str

    question_id: str

    statement: str

    prior: float

    confidence: float

    explanatory_power: float

    novelty: float

    testability: float

    risk: float


class HypothesisEngine:

    def generate(
        self,
        question: ResearchQuestion
    ) -> List[Hypothesis]:

        templates = [

            "存在未建模的结构变化",

            "存在外部冲击",

            "原有模型存在系统性偏差",

            "观测过程存在测量误差",

        ]

        prior = 1.0 / len(
            templates
        )

        hypotheses = []

        for i, statement in enumerate(
            templates
        ):

            hypotheses.append(

                Hypothesis(

                    id=f"{question.id}-H{i+1}",

                    question_id=question.id,

                    statement=statement,

                    prior=prior,

                    confidence=prior,

                    explanatory_power=0.5,

                    novelty=0.5,

                    testability=0.7,

                    risk=question.risk
                )
            )

        return hypotheses


# =========================================================
# 8. BAYESIAN UPDATE
# =========================================================

class BayesianUpdater:

    def update(
        self,
        prior,
        likelihood_if_true,
        likelihood_if_false
    ):

        numerator = (
            likelihood_if_true
            * prior
        )

        denominator = (
            numerator
            + likelihood_if_false
            * (1.0 - prior)
        )

        if denominator == 0:

            return prior

        return clamp(
            numerator / denominator
        )


# =========================================================
# 9. WORLD MODELS
# =========================================================

@dataclass
class ModelGenome:

    model_id: str

    parameters: Dict[str, float]

    complexity: float = 0.5

    robustness: float = 0.5

    confidence: float = 0.5


class BaseWorldModel:

    def __init__(
        self,
        genome: ModelGenome
    ):

        self.genome = genome

    @property
    def model_id(self):

        return self.genome.model_id

    def predict(
        self,
        world: WorldState
    ):

        raise NotImplementedError


class LinearWorldModel(
    BaseWorldModel
):

    def predict(
        self,
        world
    ):

        params = self.genome.parameters

        output = dict(
            world.variables
        )

        growth = params.get(
            "growth",
            0.02
        )

        energy_shock = params.get(
            "energy_shock",
            0.0
        )

        if "economic_growth" in output:

            output[
                "economic_growth"
            ] += (
                growth
                - energy_shock
            )

        return output


class CoupledWorldModel(
    BaseWorldModel
):

    def predict(
        self,
        world
    ):

        p = self.genome.parameters

        output = dict(
            world.variables
        )

        ai = world.get(
            "ai_capability",
            0.5
        )

        energy = world.get(
            "energy_stress",
            0.5
        )

        geopolitics = world.get(
            "geopolitical_risk",
            0.5
        )

        coupling = p.get(
            "coupling",
            0.2
        )

        output[
            "energy_stress"
        ] = clamp(
            energy
            + coupling * ai
            + 0.05 * geopolitics
        )

        output[
            "economic_growth"
        ] = clamp(

            world.get(
                "economic_growth",
                0.5
            )

            + p.get(
                "growth",
                0.02
            )

            - 0.12 * energy

            - 0.08 * geopolitics
        )

        return output


# =========================================================
# 10. MODEL ARENA
# =========================================================

@dataclass
class PredictionRecord:

    model_id: str

    timestamp: int

    target: str

    predicted: float

    confidence: float

    horizon: int


class ModelArena:

    def __init__(self):

        self.models = {}

        self.scores = {}

        self.predictions = []

    def register(
        self,
        model
    ):

        self.models[
            model.model_id
        ] = model

    def predict_all(
        self,
        world,
        target,
        timestamp
    ):

        records = []

        for model in self.models.values():

            prediction = model.predict(
                world
            ).get(
                target,
                world.get(target)
            )

            record = PredictionRecord(

                model_id=model.model_id,

                timestamp=timestamp,

                target=target,

                predicted=prediction,

                confidence=model.genome.confidence,

                horizon=1
            )

            records.append(record)

            self.predictions.append(
                record
            )

        return records

    def evaluate(
        self,
        reality
    ):

        result = {}

        for record in self.predictions:

            if record.target not in reality:
                continue

            error = abs(
                record.predicted
                - reality[record.target]
            )

            score = clamp(
                1.0 - error
            )

            old = self.scores.get(
                record.model_id,
                score
            )

            new_score =