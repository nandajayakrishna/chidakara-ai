from typing import List, Dict, Any
from organization.models.org_graph import org_graph_instance

class OrganizationReasoner:
    """
    Evaluates high-level organizational structure patterns, organizational health,
    and operational risks using graph inference.
    """
    def __init__(self, graph=org_graph_instance):
        self.graph = graph

    def reason_about_health(self) -> Dict[str, Any]:
        """
        Reasons about organizational health and risks.
        Returns a structured report.
        """
        # Count node labels
        types = {}
        for node in self.graph._nodes.values():
            types[node.label] = types.get(node.label, 0) + 1

        # Check department skill counts
        # Department -> Team -> Person -> Skill
        # In our graph: Team belongs to Dept. Person is part of Team. Person has Skill.
        dept_skills = {}
        for edge in self.graph._edges:
            if edge.predicate == "BELONG_TO":
                team = edge.source
                dept = edge.target
                
                # Find members of this team
                members = []
                for m_edge in self.graph._edges:
                    if m_edge.predicate == "PART_OF" and m_edge.target == team:
                        members.append(m_edge.source)
                
                # Find skills of these members
                skills = set()
                for member in members:
                    for s_edge in self.graph._edges:
                        if s_edge.predicate == "POSSESSES" and s_edge.source == member:
                            skills.add(s_edge.target)
                
                dept_skills[dept] = dept_skills.get(dept, set()).union(skills)

        dept_skill_report = {}
        for dept, skills in dept_skills.items():
            dept_node = self.graph._nodes.get(dept)
            dept_name = dept_node.properties.get("name", dept) if dept_node else dept
            dept_skill_report[dept_name] = len(skills)

        # Operational risk metrics
        total_projects = types.get("Project", 0)
        blocked_projects = 0
        for node in self.graph._nodes.values():
            if node.label == "Project" and node.properties.get("status") == "Blocked":
                blocked_projects += 1

        risk_score = 0.0
        if total_projects > 0:
            risk_score = (blocked_projects / total_projects) * 100.0

        return {
            "organizational_structure_summary": {
                "total_departments": types.get("Department", 0),
                "total_teams": types.get("Team", 0),
                "total_personnel": types.get("Person", 0),
                "total_projects": total_projects,
                "total_skills": types.get("Skill", 0)
            },
            "departmental_skill_coverage": dept_skill_report,
            "overall_operational_risk": {
                "score_percent": round(risk_score, 1),
                "blocked_projects_count": blocked_projects,
                "rating": "High" if risk_score > 30 else "Medium" if risk_score > 10 else "Low"
            }
        }
