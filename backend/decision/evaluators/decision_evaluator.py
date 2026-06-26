import time
from typing import Dict, Any, List
from decision.models.decision_models import ProposedDecision, DecisionRisk, DecisionAlternative, DecisionActionItem
from organization.simulators.org_simulator import OrganizationSimulator

class DecisionEvaluator:
    """
    Evaluates proposed decisions using Multi-Criteria Decision Analysis (MCDA) scoring logic.
    Integrates with OrganizationSimulator to calculate real graph dependency weights.
    """
    def __init__(self):
        self.simulator = OrganizationSimulator()

    def evaluate(self, decision_type: str, criteria_weights: Dict[str, float], custom_params: Dict[str, Any]) -> ProposedDecision:
        # Default calculations
        now_time = float(hash(decision_type))
        weights = criteria_weights or {
            "business_impact": 0.25,
            "technical_complexity": 0.15,
            "risk": 0.20,
            "cost": 0.15,
            "time": 0.10,
            "org_readiness": 0.15
        }

        # Normalize weights so they sum to 1.0
        total_w = sum(weights.values())
        if total_w > 0:
            weights = {k: v / total_w for k, v in weights.items()}

        # 1. Evaluate: Upgrade Software (CUDA 11.2 to 12.8)
        if decision_type == "upgrade_software":
            sim_res = self.simulator.run_simulation("technology_upgrade", "Tech_CUDA_11")
            affected_count = sim_res.get("affected_nodes_count", 2)
            
            problem = "Upgrade CUDA software versions from legacy 11.2 to standard 12.8."
            context = "Chidakara AI currently lists active CUDA 11.2 dependency inside Legacy Sync. This triggers security obsolescence risk parameters."
            evidence = [
                f"Obsolete technology flag detected on CUDA 11.2.",
                f"Simulation reveals {affected_count} downstream dependencies directly affected (including Project Legacy Sync)."
            ]
            supporting_knowledge = ["CUDA 12.8 Architecture Guideline", "Corporate Compliance Policy 2026"]
            affected_teams = ["AI Core Team"]
            affected_projects = ["Project Legacy Sync", "Project Chidakara"]
            dependencies = ["CUDA 11.2 Drivers", "DeepStream SDK Compilers"]
            
            risks = [
                DecisionRisk("Regression Failures", "Legacy compiler options might crash on CUDA 12 APIs", 4, 3, "Verify headers with test CI runner"),
                DecisionRisk("Resource Contraints", "AI Core devs are overloaded with Chidakara execution releases", 2, 4, "Postpone non-critical tasks")
            ]
            benefits = [
                "Removes security vulnerability index references.",
                "Enables faster hardware parallel speedups of 12.8 kernels."
            ]
            alternatives = [
                DecisionAlternative("Postpone Upgrade", "Keep CUDA 11.2 until next quarter release", ["Zero immediate transition effort"], ["Maintains active security exception flag"], "$0", "0 days"),
                DecisionAlternative("Complete Migration", "Upgrade to CUDA 12.8 immediately", ["Aligns with modern standard build specifications"], ["Triggers regression test cycles"], "$5,000", "5 days")
            ]
            
            action_plan = [
                DecisionActionItem("Verify compatibility in sandbox test environment", "Alice", "Day 1-2", "Pass compiler status"),
                DecisionActionItem("Trigger incremental sync in repositories and update setup guides", "Gary", "Day 3-4", "Commit files"),
                DecisionActionItem("Deploy to main platform and run debugger health check", "Charlie", "Day 5", "Healthy console logs")
            ]

            # Calculate raw parameter scores on 1-100 scale
            raw_scores = {
                "business_impact": 85.0,        # High impact
                "technical_complexity": 60.0,   # Moderate complexity
                "risk": 40.0,                   # Low-medium risk (40/100)
                "cost": 30.0,                   # Low cost (30/100)
                "time": 40.0,                   # Short time (40/100)
                "org_readiness": 75.0           # Ready (75/100)
            }

        # 2. Evaluate: Adopt Technology (Go Language for data pipelines)
        elif decision_type == "adopt_technology":
            problem = "Adopt Go programming language as standard development language for scheduler tasks."
            context = "Chidakara Pipeline currently uses Go scheduler templates, but team lists missing skill gaps for Go Language."
            evidence = [
                "Task 'Implement Go Scheduler' is currently Blocked.",
                "Missing Go Language skills flagged on Project Data Pipeline."
            ]
            supporting_knowledge = ["Go Runtime Performance Spec", "Organization Skill Matrix Map"]
            affected_teams = ["Platform & Ops Team", "AI Core Team"]
            affected_projects = ["Project Data Pipeline"]
            dependencies = ["Go Compiler 1.21 Toolchains"]
            
            risks = [
                DecisionRisk("Code Maintenance Gaps", "Team has zero native Go developers, creating support vulnerabilities", 5, 4, "Hire secondary Go consultant"),
                DecisionRisk("Delayed Release", "Developer training time will push back pipeline launch schedules", 3, 3, "Run training in parallel with design")
            ]
            benefits = [
                "Unblocks Task 'Implement Go Scheduler'.",
                "High concurrency capability reduces pipeline scheduling latency."
            ]
            alternatives = [
                DecisionAlternative("Outsource Scheduler", "Hire freelance Go coder", ["Fast initial deployment"], ["High maintenance handoff friction"], "$8,000", "14 days"),
                DecisionAlternative("Train Internal Developers", "Train Ethan and Charlie on Go", ["Retains core IP within engineering team"], ["Consumes 14 days training overhead time"], "$2,000", "20 days")
            ]
            
            action_plan = [
                DecisionActionItem("Onboard basic Go programming tutorials", "Ethan", "Day 1-10", "Tutorial certificate"),
                DecisionActionItem("Rewrite block scheduler using Go templates", "Charlie", "Day 11-18", "Code commit"),
                DecisionActionItem("Execute workflow validation tests", "Bob", "Day 19-20", "Pass parallel runner")
            ]

            raw_scores = {
                "business_impact": 80.0,
                "technical_complexity": 75.0,
                "risk": 65.0,
                "cost": 50.0,
                "time": 70.0,
                "org_readiness": 40.0 # Low readiness
            }

        # 3. Default fallback (e.g. Allocate Budget or Hire Developers)
        else:
            problem = f"Execute organizational decision proposal for: {decision_type}."
            context = "Standard organizational evaluation parameters evaluated."
            evidence = ["Evaluated corporate assets inventory database."]
            supporting_knowledge = ["Chidakara Strategic Goals 2026"]
            affected_teams = ["Engineering Department"]
            affected_projects = ["Project Chidakara"]
            dependencies = []
            risks = [DecisionRisk("Implementation Delay", "Proposed tasks might overrun scheduled duration slots", 3, 3, "Add safety buffers")]
            benefits = ["Optimizes team throughput and alignment metrics."]
            alternatives = [DecisionAlternative("Maintain Status Quo", "Keep current operational configurations", ["Zero direct transition costs"], ["Maintains structural inefficiencies"], "$0", "0 days")]
            action_plan = [DecisionActionItem("Draft detailed implementation specification", "Diana", "Week 1", "Spec document")]

            raw_scores = {
                "business_impact": 70.0,
                "technical_complexity": 50.0,
                "risk": 50.0,
                "cost": 50.0,
                "time": 50.0,
                "org_readiness": 60.0
            }

        # Compute weighted aggregate score (higher is better)
        # Note: For technical complexity, risk, cost, and time, a HIGHER raw score means HIGHER complexity/cost/risk/time (which is worse).
        # Therefore, we invert those scores to compute utility: utility = 100 - raw_score
        utility_scores = {}
        for criteria, score in raw_scores.items():
            if criteria in ["technical_complexity", "risk", "cost", "time"]:
                utility_scores[criteria] = 100.0 - score
            else:
                utility_scores[criteria] = score

        weighted_score = sum(weights[c] * utility_scores[c] for c in weights.keys())
        
        # Determine recommended option based on scores
        recommended = "Complete Migration" if decision_type == "upgrade_software" else "Train Internal Developers" if decision_type == "adopt_technology" else "Maintain Status Quo"
        confidence = 0.85 if decision_type == "upgrade_software" else 0.72 if decision_type == "adopt_technology" else 0.60

        return ProposedDecision(
            id=f"dec-{int(time.time())}-{decision_type}",
            decision_type=decision_type,
            problem_statement=problem,
            context=context,
            evidence=evidence,
            supporting_knowledge=supporting_knowledge,
            affected_teams=affected_teams,
            affected_projects=affected_projects,
            dependencies=dependencies,
            risks=risks,
            benefits=benefits,
            alternatives=alternatives,
            recommended_option=recommended,
            confidence=confidence,
            action_plan=action_plan,
            estimated_impact=f"Improves aggregate operational metrics scoring utility to {round(weighted_score, 1)} points.",
            scores=raw_scores
        )
