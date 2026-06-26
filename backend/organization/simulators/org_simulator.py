from typing import List, Dict, Any
from organization.models.org_graph import org_graph_instance

class OrganizationSimulator:
    """
    Simulates changes in the organization graph and analyzes cascading dependency impacts.
    """
    def __init__(self, graph=org_graph_instance):
        self.graph = graph

    def run_simulation(self, scenario_type: str, target_id: str) -> Dict[str, Any]:
        """
        Runs a simulation given a scenario type and target entity ID.
        """
        # Normalize target ID
        target_node = self.graph._nodes.get(target_id)
        if not target_node:
            # Try finding by name in properties
            for nid, node in self.graph._nodes.items():
                if node.properties.get("name", "").lower() == target_id.lower():
                    target_id = nid
                    target_node = node
                    break

        if not target_node:
            return {
                "success": False,
                "error": f"Target entity '{target_id}' not found in the organization graph."
            }

        target_name = target_node.properties.get("name", target_id)
        target_type = target_node.label

        affected_nodes = []
        dependency_chains = []
        summary = ""
        risk_level = "Low"

        # 1. Simulate: Project Delayed
        if scenario_type == "project_delay":
            risk_level = "Medium"
            # Find downstream products and customers
            # Project -> Part Of -> Product -> Sold To -> Customer
            products = []
            customers = []
            
            # Find products
            for edge in self.graph._edges:
                if edge.predicate == "PART_OF" and edge.source == target_id:
                    prod_node = self.graph._nodes.get(edge.target)
                    if prod_node and prod_node.label == "Product":
                        products.append(prod_node)
                        affected_nodes.append({
                            "id": prod_node.id,
                            "name": prod_node.properties.get("name"),
                            "type": prod_node.label,
                            "relation": "Part Of Product"
                        })
                        dependency_chains.append(f"{target_name} -> {prod_node.properties.get('name')}")

            # Find customers
            for prod in products:
                for edge in self.graph._edges:
                    if edge.predicate == "SOLD_TO" and edge.source == prod.id:
                        cust_node = self.graph._nodes.get(edge.target)
                        if cust_node and cust_node.label == "Customer":
                            customers.append(cust_node)
                            affected_nodes.append({
                                "id": cust_node.id,
                                "name": cust_node.properties.get("name"),
                                "type": cust_node.label,
                                "relation": "Delivery Dependency"
                            })
                            dependency_chains.append(f"{target_name} -> {prod.properties.get('name')} -> {cust_node.properties.get('name')}")

            # Find tasks of project
            for edge in self.graph._edges:
                if edge.predicate == "PART_OF" and edge.target == target_id:
                    task_node = self.graph._nodes.get(edge.source)
                    if task_node and task_node.label == "Task":
                        affected_nodes.append({
                            "id": task_node.id,
                            "name": task_node.properties.get("name"),
                            "type": task_node.label,
                            "relation": "Associated Task"
                        })

            cust_names = [c.properties.get("name") for c in customers]
            prod_names = [p.properties.get("name") for p in products]
            summary = f"Delaying '{target_name}' pushes back target release timelines for downstream products: {', '.join(prod_names)}. This creates immediate delivery risks for key customers: {', '.join(cust_names)}."

        # 2. Simulate: Engineer Leaves
        elif scenario_type == "engineer_leave":
            risk_level = "High"
            # Person -> Works On -> Project -> Part Of -> Product
            # Person -> lead of -> Team
            projects = []
            tasks = []
            teams = []

            # Lead of teams
            for nid, node in self.graph._nodes.items():
                if node.label == "Team" and node.properties.get("lead") == target_id:
                    teams.append(node)
                    affected_nodes.append({
                        "id": nid,
                        "name": node.properties.get("name"),
                        "type": node.label,
                        "relation": "Team Leadership Link"
                    })
                    dependency_chains.append(f"{target_name} (Lead) -> {node.properties.get('name')}")

            # Works on projects
            for edge in self.graph._edges:
                if edge.predicate == "WORKS_ON" and edge.source == target_id:
                    proj_node = self.graph._nodes.get(edge.target)
                    if proj_node:
                        projects.append(proj_node)
                        affected_nodes.append({
                            "id": proj_node.id,
                            "name": proj_node.properties.get("name"),
                            "type": proj_node.label,
                            "relation": "Assigned Developer"
                        })
                        dependency_chains.append(f"{target_name} -> {proj_node.properties.get('name')}")

            # Assigned tasks
            for edge in self.graph._edges:
                if edge.predicate == "ASSIGNED_TO" and edge.target == target_id:
                    task_node = self.graph._nodes.get(edge.source)
                    if task_node:
                        tasks.append(task_node)
                        affected_nodes.append({
                            "id": task_node.id,
                            "name": task_node.properties.get("name"),
                            "type": task_node.label,
                            "relation": "Assigned Active Task"
                        })
                        dependency_chains.append(f"{target_name} -> Task: {task_node.properties.get('name')}")

            # Check single point of failure skills on these projects
            spof_skills = []
            for proj in projects:
                # Find project required skills
                proj_skills = []
                for edge in self.graph._edges:
                    if edge.predicate == "REQUIRED_BY" and edge.target == proj.id:
                        proj_skills.append(edge.source)

                for skill in proj_skills:
                    # Find other devs on project with this skill
                    other_possessors = []
                    for edge in self.graph._edges:
                        if edge.predicate == "WORKS_ON" and edge.target == proj.id:
                            dev = edge.source
                            if dev != target_id:
                                # Check skill
                                for s_edge in self.graph._edges:
                                    if s_edge.predicate == "POSSESSES" and s_edge.source == dev and s_edge.target == skill:
                                        other_possessors.append(dev)
                    
                    # Target developer possesses this skill
                    has_skill = False
                    for s_edge in self.graph._edges:
                        if s_edge.predicate == "POSSESSES" and s_edge.source == target_id and s_edge.target == skill:
                            has_skill = True
                            break

                    if has_skill and not other_possessors:
                        skill_node = self.graph._nodes.get(skill)
                        sname = skill_node.properties.get("name") if skill_node else skill
                        spof_skills.append(f"'{sname}' on {proj.properties.get('name')}")

            proj_names = [p.properties.get("name") for p in projects]
            task_names = [t.properties.get("name") for t in tasks]
            
            spof_text = ""
            if spof_skills:
                spof_text = f" Critical Skill SPOFs lost: {', '.join(spof_skills)}."

            summary = f"Departure of {target_name} disrupts {len(projects)} projects ({', '.join(proj_names)}) and stalls {len(tasks)} active tasks ({', '.join(task_names)}).{spof_text}"

        # 3. Simulate: CUDA Upgraded / Technology Upgraded
        elif scenario_type == "technology_upgrade":
            risk_level = "Medium"
            # Technology -> Project -> Repositories
            projects = []
            
            for edge in self.graph._edges:
                if edge.predicate == "USES" and edge.target == target_id:
                    proj_node = self.graph._nodes.get(edge.source)
                    if proj_node:
                        projects.append(proj_node)
                        affected_nodes.append({
                            "id": proj_node.id,
                            "name": proj_node.properties.get("name"),
                            "type": proj_node.label,
                            "relation": "Uses Technology"
                        })
                        dependency_chains.append(f"{target_name} (Upgrade) -> {proj_node.properties.get('name')}")

            # Find downstream repositories
            for proj in projects:
                for edge in self.graph._edges:
                    if edge.predicate == "GENERATES" and edge.source == proj.id:
                        doc_node = self.graph._nodes.get(edge.target)
                        if doc_node:
                            affected_nodes.append({
                                "id": doc_node.id,
                                "name": doc_node.properties.get("name"),
                                "type": doc_node.label,
                                "relation": "Generated Document"
                            })
                            dependency_chains.append(f"{target_name} -> {proj.properties.get('name')} -> Doc: {doc_node.properties.get('name')}")

            proj_names = [p.properties.get("name") for p in projects]
            summary = f"Upgrading technology '{target_name}' triggers regression test cycles on projects: {', '.join(proj_names)}. Documentation updates will be required for associated architectural guides."

        # 4. Simulate: Document Changed
        elif scenario_type == "document_change":
            risk_level = "Low"
            # Document -> References -> Document
            # Project -> Generates -> Document (Incoming)
            referencing_docs = []
            
            for edge in self.graph._edges:
                if edge.predicate == "REFERENCES" and edge.target == target_id:
                    ref_doc = self.graph._nodes.get(edge.source)
                    if ref_doc:
                        referencing_docs.append(ref_doc)
                        affected_nodes.append({
                            "id": ref_doc.id,
                            "name": ref_doc.properties.get("name"),
                            "type": ref_doc.label,
                            "relation": "References Document"
                        })
                        dependency_chains.append(f"{target_name} (Modified) -> {ref_doc.properties.get('name')}")

            # Find projects generating referencing docs
            for rd in referencing_docs:
                for edge in self.graph._edges:
                    if edge.predicate == "GENERATES" and edge.target == rd.id:
                        proj_node = self.graph._nodes.get(edge.source)
                        if proj_node:
                            affected_nodes.append({
                                "id": proj_node.id,
                                "name": proj_node.properties.get("name"),
                                "type": proj_node.label,
                                "relation": "Project Compliance"
                            })
                            dependency_chains.append(f"{target_name} -> {rd.properties.get('name')} -> Project: {proj_node.properties.get('name')}")

            ref_names = [r.properties.get("name") for r in referencing_docs]
            if ref_names:
                summary = f"Modifying '{target_name}' invalidates configuration schemas in downstream guides: {', '.join(ref_names)}. Requires immediate content audits."
            else:
                summary = f"Modifying '{target_name}' has low cascading impact. No active referencing documents found in the current graph."

        # 5. Simulate: Technology Removed
        elif scenario_type == "technology_removal":
            risk_level = "High"
            # Technology -> Project (breaks compile)
            projects = []
            
            for edge in self.graph._edges:
                if edge.predicate == "USES" and edge.target == target_id:
                    proj_node = self.graph._nodes.get(edge.source)
                    if proj_node:
                        projects.append(proj_node)
                        affected_nodes.append({
                            "id": proj_node.id,
                            "name": proj_node.properties.get("name"),
                            "type": proj_node.label,
                            "relation": "Critical Code Block"
                        })
                        dependency_chains.append(f"Remove {target_name} -> {proj_node.properties.get('name')} (Stalled)")

            proj_names = [p.properties.get("name") for p in projects]
            summary = f"Removing technology '{target_name}' breaks build dependency chains for active projects: {', '.join(proj_names)}. These projects must migrate to an alternative standard immediately."

        else:
            summary = f"Generic simulation triggered on '{target_name}' ({target_type}). Cascading dependency traversal completed."

        return {
            "success": True,
            "scenario": scenario_type,
            "target_id": target_id,
            "target_name": target_name,
            "target_type": target_type,
            "risk_level": risk_level,
            "summary": summary,
            "affected_nodes_count": len(affected_nodes),
            "affected_nodes": affected_nodes,
            "dependency_chains": dependency_chains
        }
