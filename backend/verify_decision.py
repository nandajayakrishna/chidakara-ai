import sys
from decision.evaluators.decision_evaluator import DecisionEvaluator
from decision.strategies.strategy_engine import StrategyEngine
from decision.reports.report_generator import ReportGenerator

def run_tests():
    print("====================================")
    print("Verifying Decision Evaluator MCDA Scoring")
    print("====================================")
    evaluator = DecisionEvaluator()
    
    # Test Upgrade Software decision
    weights = {
        "business_impact": 0.25,
        "technical_complexity": 0.15,
        "risk": 0.20,
        "cost": 0.15,
        "time": 0.10,
        "org_readiness": 0.15
    }
    decision = evaluator.evaluate("upgrade_software", weights, {})
    
    print(f"Decision ID: {decision.id}")
    print(f"Problem: {decision.problem_statement}")
    print(f"Recommended Option: {decision.recommended_option}")
    print(f"Confidence: {decision.confidence}")
    print(f"Scores: {decision.scores}")
    
    assert decision.recommended_option == "Complete Migration", "Incorrect recommendation option"
    assert decision.confidence == 0.85, "Incorrect confidence rating"
    assert "business_impact" in decision.scores, "Scores dictionary missing business_impact"
    
    print("[OK] Decision Evaluator MCDA Scoring check passed.")

    print("\n====================================")
    print("Verifying Strategy Profile Comparison")
    print("====================================")
    engine = StrategyEngine()
    comparison = engine.compare_strategies(decision)
    
    print(f"Recommended Posture Profile: {comparison['recommended_strategy_profile']}")
    print(f"Explanation: {comparison['recommended_strategy_explanation']}")
    
    for name, detail in comparison['comparisons'].items():
        print(f" - {name} Aggregate Score: {detail['aggregate_score']}")
        assert "aggregate_score" in detail, "Score missing for profile"
        
    print("[OK] Strategy Profile Comparison check passed.")

    print("\n====================================")
    print("Verifying Executive Report Generation")
    print("====================================")
    report_gen = ReportGenerator()
    report = report_gen.generate_report(decision, comparison)
    
    print("Executive Summary in Report:")
    lines = report.split("\n")
    for line in lines[:10]:
        if line.strip():
            print(f"  {line}")
            
    assert "# Executive Decision Intelligence Report" in report, "Header missing in report"
    assert "## 1. Executive Summary" in report, "Summary section missing in report"
    print("[OK] Executive Report check passed.")

    print("\nALL DECISION INTELLIGENCE MODULE TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
