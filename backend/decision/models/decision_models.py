from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class DecisionTemplate:
    id: str
    name: str
    description: str
    default_criteria_weights: Dict[str, float] = field(default_factory=lambda: {
        "business_impact": 0.25,
        "technical_complexity": 0.15,
        "risk": 0.20,
        "cost": 0.15,
        "time": 0.10,
        "org_readiness": 0.15
    })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DecisionAlternative:
    name: str
    description: str
    pros: List[str]
    cons: List[str]
    estimated_cost: str
    estimated_time: str

@dataclass
class DecisionRisk:
    name: str
    description: str
    probability: int # 1 to 5
    impact: int # 1 to 5
    mitigation: str

@dataclass
class DecisionActionItem:
    task: str
    owner: str
    timeline: str
    kpi: str

@dataclass
class ProposedDecision:
    id: str
    decision_type: str # upgrade_software, adopt_tech, hire_dev, etc.
    problem_statement: str
    context: str
    evidence: List[str]
    supporting_knowledge: List[str]
    affected_teams: List[str]
    affected_projects: List[str]
    dependencies: List[str]
    risks: List[DecisionRisk]
    benefits: List[str]
    alternatives: List[DecisionAlternative]
    recommended_option: str
    confidence: float # 0.0 to 1.0
    action_plan: List[DecisionActionItem]
    estimated_impact: str
    scores: Dict[str, float] # Weighted criteria scores

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Ensure sub dataclasses serialize properly
        d["risks"] = [asdict(r) for r in self.risks]
        d["alternatives"] = [asdict(a) for a in self.alternatives]
        d["action_plan"] = [asdict(ai) for ai in self.action_plan]
        return d
