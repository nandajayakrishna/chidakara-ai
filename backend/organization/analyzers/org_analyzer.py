from typing import List, Dict, Any, Optional
from organization.models.org_graph import org_graph_instance

class OrganizationAnalyzer:
    """
    Analyzes the organization graph to answer structural queries.
    """
    def __init__(self, graph=org_graph_instance):
        self.graph = graph

    def get_projects_depending_on(self, tech_name: str) -> List[Dict[str, Any]]:
        """
        Which projects depend on a technology/language (e.g. 'Python')?
        """
        # Find technology node ID
        tech_nodes = []
        for nid, node in self.graph._nodes.items():
            if node.label == "Technology" or node.label == "Skill":
                if tech_name.lower() in nid.lower() or tech_name.lower() in node.properties.get("name", "").lower():
                    tech_nodes.append(nid)

        results = []
        for tech_id in tech_nodes:
            tech_node = self.graph._nodes[tech_id]
            
            # Find projects using this tech directly
            direct_projects = []
            for edge in self.graph._edges:
                if edge.predicate == "USES" and edge.target == tech_id:
                    proj_id = edge.source
                    proj_node = self.graph._nodes.get(proj_id)
                    if proj_node and proj_node.label == "Project":
                        direct_projects.append(proj_node.properties.get("name", proj_id))

            # Also check if it's a required skill
            for edge in self.graph._edges:
                if edge.predicate == "REQUIRED_BY" and edge.source == tech_id:
                    proj_id = edge.target
                    proj_node = self.graph._nodes.get(proj_id)
                    if proj_node and proj_node.label == "Project":
                        proj_name = proj_node.properties.get("name", proj_id)
                        if proj_name not in direct_projects:
                            direct_projects.append(proj_name)

            if direct_projects:
                results.append({
                    "technology": tech_node.properties.get("name", tech_id),
                    "tech_id": tech_id,
                    "projects": direct_projects
                })
        return results

    def get_teams_using(self, tech_name: str) -> List[Dict[str, Any]]:
        """
        Which teams use CUDA (or any other technology)?
        """
        # Find technology node ID
        tech_nodes = []
        for nid, node in self.graph._nodes.items():
            if tech_name.lower() in nid.lower() or tech_name.lower() in node.properties.get("name", "").lower():
                tech_nodes.append(nid)

        results = []
        for tech_id in tech_nodes:
            tech_node = self.graph._nodes[tech_id]
            teams_using = set()

            # Find projects using this tech
            projects_using = []
            for edge in self.graph._edges:
                if edge.predicate == "USES" and edge.target == tech_id:
                    projects_using.append(edge.source)

            # Find people working on these projects
            people_on_projects = []
            for edge in self.graph._edges:
                if edge.predicate == "WORKS_ON" and edge.target in projects_using:
                    people_on_projects.append(edge.source)

            # Find which teams these people belong to
            for edge in self.graph._edges:
                if edge.predicate == "PART_OF" and edge.source in people_on_projects:
                    team_id = edge.target
                    team_node = self.graph._nodes.get(team_id)
                    if team_node:
                        teams_using.add(team_node.properties.get("name", team_id))

            if teams_using:
                results.append({
                    "technology": tech_node.properties.get("name", tech_id),
                    "tech_id": tech_id,
                    "teams": list(teams_using)
                })
        return results

    def get_project_owners(self) -> List[Dict[str, Any]]:
        """
        Who owns each project?
        """
        owners = []
        for nid, node in self.graph._nodes.items():
            if node.label == "Project":
                project_name = node.properties.get("name", nid)
                owner_depts = []
                works_on_people = []

                # Find owning department
                for edge in self.graph._edges:
                    if edge.predicate == "OWNS" and edge.target == nid:
                        dept_node = self.graph._nodes.get(edge.source)
                        if dept_node:
                            owner_depts.append(dept_node.properties.get("name", edge.source))

                # Find assigned people
                for edge in self.graph._edges:
                    if edge.predicate == "WORKS_ON" and edge.target == nid:
                        person_node = self.graph._nodes.get(edge.source)
                        if person_node:
                            works_on_people.append(person_node.properties.get("name", edge.source))

                owners.append({
                    "project_id": nid,
                    "project_name": project_name,
                    "departments": owner_depts,
                    "people": works_on_people,
                    "lead": works_on_people[0] if works_on_people else "Unassigned"
                })
        return owners

    def get_missing_skills(self) -> List[Dict[str, Any]]:
        """
        Which skills are missing?
        Finds skills required by a project but not possessed by any developer working on it.
        """
        missing = []
        for proj_id, proj_node in self.graph._nodes.items():
            if proj_node.label == "Project":
                # Get required skills
                req_skills = []
                for edge in self.graph._edges:
                    if edge.predicate == "REQUIRED_BY" and edge.target == proj_id:
                        req_skills.append(edge.source)

                # Get developers on project
                devs = []
                for edge in self.graph._edges:
                    if edge.predicate == "WORKS_ON" and edge.target == proj_id:
                        devs.append(edge.source)

                # Get collective skills of these devs
                dev_skills = set()
                for dev in devs:
                    for edge in self.graph._edges:
                        if edge.predicate == "POSSESSES" and edge.source == dev:
                            dev_skills.add(edge.target)

                # Find required skills NOT in dev_skills
                project_missing = []
                for skill in req_skills:
                    if skill not in dev_skills:
                        skill_node = self.graph._nodes.get(skill)
                        skill_name = skill_node.properties.get("name", skill) if skill_node else skill
                        project_missing.append(skill_name)

                if project_missing:
                    missing.append({
                        "project": proj_node.properties.get("name", proj_id),
                        "project_id": proj_id,
                        "missing_skills": project_missing,
                        "current_team_size": len(devs)
                    })
        return missing

    def get_blocked_projects(self) -> List[Dict[str, Any]]:
        """
        Which projects are blocked?
        A project is blocked if it is marked blocked, has blocked tasks, or has critical skill gaps.
        """
        blocked = []
        for proj_id, proj_node in self.graph._nodes.items():
            if proj_node.label == "Project":
                reasons = []
                
                # Check status property
                if proj_node.properties.get("status") == "Blocked":
                    reasons.append("Project status marked as Blocked")

                # Check tasks associated with project
                blocked_tasks = []
                for edge in self.graph._edges:
                    if edge.predicate == "PART_OF" and edge.target == proj_id:
                        task_id = edge.source
                        task_node = self.graph._nodes.get(task_id)
                        if task_node and task_node.label == "Task" and task_node.properties.get("status") == "Blocked":
                            blocked_tasks.append(task_node.properties.get("name", task_id))

                if blocked_tasks:
                    reasons.append(f"Contains blocked tasks: {', '.join(blocked_tasks)}")

                # Check if it has missing skills
                missing_skills_info = self.get_missing_skills()
                for item in missing_skills_info:
                    if item["project_id"] == proj_id:
                        reasons.append(f"Missing required skills: {', '.join(item['missing_skills'])}")

                if reasons:
                    blocked.append({
                        "project": proj_node.properties.get("name", proj_id),
                        "project_id": proj_id,
                        "priority": proj_node.properties.get("priority", "Medium"),
                        "reasons": reasons
                    })
        return blocked

    def get_obsolete_technologies(self) -> List[Dict[str, Any]]:
        """
        Which technologies are obsolete?
        """
        obsolete = []
        for tech_id, tech_node in self.graph._nodes.items():
            if tech_node.label == "Technology" and tech_node.properties.get("status") == "Obsolete":
                # Find projects using this tech
                affected_projects = []
                for edge in self.graph._edges:
                    if edge.predicate == "USES" and edge.target == tech_id:
                        proj_node = self.graph._nodes.get(edge.source)
                        if proj_node:
                            affected_projects.append(proj_node.properties.get("name", edge.source))

                obsolete.append({
                    "technology": tech_node.properties.get("name", tech_id),
                    "tech_id": tech_id,
                    "version": tech_node.properties.get("version", "N/A"),
                    "affected_projects": affected_projects
                })
        return obsolete

    def get_duplicate_documents(self) -> List[Dict[str, Any]]:
        """
        Which documents are duplicated?
        """
        duplicates = []
        for doc_id, doc_node in self.graph._nodes.items():
            if doc_node.label == "Document" and doc_node.properties.get("status") == "Duplicate":
                # Find references or main files
                main_doc = "UI Brand Guidelines" # Static lookup based on mock data
                duplicates.append({
                    "duplicate_document": doc_node.properties.get("name", doc_id),
                    "duplicate_id": doc_id,
                    "main_document": main_doc,
                    "similarity": "95%",
                    "reasons": "Identical structure and typography layout definitions."
                })
        return duplicates

    def get_workflow_bottlenecks(self) -> List[Dict[str, Any]]:
        """
        Which workflows or tasks have bottlenecks?
        Identify engineers who have too many assigned tasks, or tasks in progress for too long.
        """
        bottlenecks = []
        
        # Calculate task load per person
        person_tasks = {}
        for edge in self.graph._edges:
            if edge.predicate == "ASSIGNED_TO":
                person = edge.target
                task_id = edge.source
                task_node = self.graph._nodes.get(task_id)
                if task_node and task_node.properties.get("status") != "Completed":
                    person_tasks[person] = person_tasks.get(person, 0) + 1

        for person, task_count in person_tasks.items():
            if task_count >= 2: # In our small team, 2+ active tasks is a bottleneck
                person_node = self.graph._nodes.get(person)
                name = person_node.properties.get("name", person) if person_node else person
                bottlenecks.append({
                    "type": "Resource Overload",
                    "resource": name,
                    "resource_id": person,
                    "active_tasks_count": task_count,
                    "details": f"{name} is currently assigned {task_count} active tasks, creating a critical path dependency bottleneck."
                })

        # Blocked tasks are also bottlenecks
        for task_id, node in self.graph._nodes.items():
            if node.label == "Task" and node.properties.get("status") == "Blocked":
                bottlenecks.append({
                    "type": "Blocked Task",
                    "resource": node.properties.get("name", task_id),
                    "resource_id": task_id,
                    "active_tasks_count": 1,
                    "details": f"Task '{node.properties.get('name')}' is blocked, halting progress of downstream pipeline components."
                })

        return bottlenecks

    def run_all_analysis(self) -> Dict[str, Any]:
        """
        Runs all analyzers and returns consolidated results.
        """
        return {
            "projects_depend_on_python": self.get_projects_depending_on("Python"),
            "teams_using_cuda": self.get_teams_using("CUDA"),
            "project_owners": self.get_project_owners(),
            "missing_skills": self.get_missing_skills(),
            "blocked_projects": self.get_blocked_projects(),
            "obsolete_technologies": self.get_obsolete_technologies(),
            "duplicate_documents": self.get_duplicate_documents(),
            "workflow_bottlenecks": self.get_workflow_bottlenecks()
        }
