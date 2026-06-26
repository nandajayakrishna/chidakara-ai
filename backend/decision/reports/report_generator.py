from typing import Dict, Any
from decision.models.decision_models import ProposedDecision

class ReportGenerator:
    """
    Compiles detailed, print-ready executive reports from ProposedDecision evaluation results.
    """
    def generate_report(self, decision: ProposedDecision, comparison: Dict[str, Any]) -> str:
        # Build Executive Summary
        exec_summary = f"Proposed decision analysis regarding: **{decision.problem_statement}**. " \
                       f"Based on a multi-criteria utility score evaluation, the recommended course of action is to select option **'{decision.recommended_option}'**."

        # Key Findings
        findings_md = ""
        for i, ev in enumerate(decision.evidence):
            findings_md += f"{i+1}. {ev}\n"

        # Risk Assessment
        risk_md = ""
        for risk in decision.risks:
            risk_md += f"* **{risk.name}** (Severity: {risk.probability * risk.impact}/25)\n" \
                       f"  * Description: {risk.description}\n" \
                       f"  * Mitigation: {risk.mitigation}\n"

        # Financial Considerations
        financial_md = ""
        for alt in decision.alternatives:
            financial_md += f"* **{alt.name}**: cost {alt.estimated_cost} | implementation timeline: {alt.estimated_time}\n"

        # Implementation Roadmap
        roadmap_md = ""
        for item in decision.action_plan:
            roadmap_md += f"* **{item.timeline}**: {item.task} (Owner: *{item.owner}*)\n"

        # KPIs
        kpis_md = ""
        for item in decision.action_plan:
            kpis_md += f"* Measure: *{item.kpi}* for task '{item.task[:30]}...'\n"

        # Full Report
        report_template = f"""# Executive Decision Intelligence Report

## 1. Executive Summary
{exec_summary}
* **Recommended Strategy Posture**: {comparison['recommended_strategy_profile']}
* **Confidence Rating**: {int(decision.confidence * 100)}%

---

## 2. Key Findings & Supporting Evidence
{findings_md}

---

## 3. Financial & Resource Considerations
{financial_md}

---

## 4. Risk Assessment & Mitigation Matrix
{risk_md}

---

## 5. Recommended Decision & Strategic Posture
* **Decision Path**: {decision.recommended_option}
* **Impact Metric**: {decision.estimated_impact}
* **Strategic Selection Explanation**: {comparison['recommended_strategy_explanation']}

---

## 6. Implementation Roadmap
{roadmap_md}

---

## 7. KPIs & Success Metrics
{kpis_md}

---

## 8. Follow-up Actions
1. Confirm credentials config with platform managers.
2. Trigger the test environment sandboxes in the Workflow Engine.
3. Track latency metrics in Visual Debugger.
"""
        return report_template
