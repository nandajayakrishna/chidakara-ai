from typing import Dict, Any, List
from decision.models.decision_models import ProposedDecision

class StrategyEngine:
    """
    Generates and compares alternative strategy profiles (postures) for a proposed decision.
    Profiles: Conservative, Balanced, Aggressive, Innovation-first, Cost-first.
    """
    def compare_strategies(self, decision: ProposedDecision) -> Dict[str, Any]:
        raw_scores = decision.scores
        
        # 1. Define weights for each strategic profile
        # Each profile weights the 6 core criteria differently
        profiles = {
            "Conservative": {
                "business_impact": 0.15,
                "technical_complexity": 0.20,
                "risk": 0.35, # Heavily penalize risk
                "cost": 0.15,
                "time": 0.05,
                "org_readiness": 0.10
            },
            "Balanced": {
                "business_impact": 0.25,
                "technical_complexity": 0.15,
                "risk": 0.20,
                "cost": 0.15,
                "time": 0.10,
                "org_readiness": 0.15
            },
            "Aggressive": {
                "business_impact": 0.40, # Heavily prioritize impact
                "technical_complexity": 0.05,
                "risk": 0.10,
                "cost": 0.10,
                "time": 0.25, # Heavily prioritize fast implementation
                "org_readiness": 0.10
            },
            "Innovation-first": {
                "business_impact": 0.25,
                "technical_complexity": 0.10,
                "risk": 0.15,
                "cost": 0.10,
                "time": 0.10,
                "org_readiness": 0.30 # Heavily prioritize org adoption readiness
            },
            "Cost-first": {
                "business_impact": 0.10,
                "technical_complexity": 0.15,
                "risk": 0.15,
                "cost": 0.40, # Heavily minimize cost
                "time": 0.15,
                "org_readiness": 0.05
            }
        }

        # Calculate utilities: Utility = 100 - raw_score for penalties
        utility_scores = {}
        for criteria, score in raw_scores.items():
            if criteria in ["technical_complexity", "risk", "cost", "time"]:
                utility_scores[criteria] = 100.0 - score
            else:
                utility_scores[criteria] = score

        # Calculate final utility scoring per profile
        comparison = {}
        best_score = -1.0
        recommended_profile = ""

        for profile_name, weights in profiles.items():
            score = sum(weights[c] * utility_scores[c] for c in weights.keys())
            rounded_score = round(score, 1)
            comparison[profile_name] = {
                "aggregate_score": rounded_score,
                "weights": weights
            }
            if score > best_score:
                best_score = score
                recommended_profile = profile_name

        # Summary descriptions
        summaries = {
            "Conservative": "Prioritizes minimal exposure to technical friction and security regressions.",
            "Balanced": "Standard corporate posture balancing budget constraints and performance objectives.",
            "Aggressive": "Maximizes business throughput velocity at the expense of elevated risk thresholds.",
            "Innovation-first": "Prioritizes developer training, toolchain upgrades, and stack modernity.",
            "Cost-first": "Enforces strict budget constraints, minimizing direct consulting and capital expenditures."
        }

        return {
            "decision_id": decision.id,
            "decision_type": decision.decision_type,
            "recommended_option": decision.recommended_option,
            "recommended_strategy_profile": recommended_profile,
            "recommended_strategy_explanation": f"The '{recommended_profile}' profile yields the highest efficiency score of {round(best_score, 1)} points. {summaries[recommended_profile]}",
            "comparisons": comparison,
            "summaries": summaries
        }
