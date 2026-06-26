from typing import List, Dict, Set, Any
from workflow.workflow_graph import WorkflowDAG

def analyze_dependencies(steps: List[str], agent_registry: Dict[str, Any]) -> WorkflowDAG:
    """
    Parses steps from the planner, maps them to agent functions, resolves dependencies,
    and returns a scheduled WorkflowDAG.
    """
    # 1. Deduplicate planner steps while preserving order
    seen = set()
    unique_steps = []
    for step in steps:
        if step not in seen and step in agent_registry:
            seen.add(step)
            unique_steps.append(step)

    # 2. Build DAG and assign dependencies based on architectural rules
    dag = WorkflowDAG()
    
    # Dependency mapping logic:
    # - Research, Graph, Web, Tool can execute independently (zero-dependencies).
    # - Knowledge waits for Research, Graph, Web, Tool.
    # - Reflection waits for Knowledge (or Tool, if Knowledge is absent).
    # - Critic waits for Reflection (or Knowledge).
    # - Memory waits for Critic.
    
    for step in unique_steps:
        deps = []
        if step == "knowledge":
            for d in ["research", "graph", "web", "tool"]:
                if d in unique_steps:
                    deps.append(d)
        elif step == "reflection":
            if "knowledge" in unique_steps:
                deps.append("knowledge")
            elif "tool" in unique_steps:
                deps.append("tool")
        elif step == "critic":
            if "reflection" in unique_steps:
                deps.append("reflection")
            elif "knowledge" in unique_steps:
                deps.append("knowledge")
        elif step == "memory":
            if "critic" in unique_steps:
                deps.append("critic")
                
        # Register node in DAG with resolved dependencies
        dag.add_node(step, agent_registry[step], deps)

    # 3. Schedule stages dynamically
    schedule_stages(dag)
    
    return dag

def schedule_stages(dag: WorkflowDAG) -> None:
    """
    Assigns parallel_group and stage_number to DAG nodes using a level-order scheduling algorithm.
    """
    nodes = dag.get_all_nodes()
    resolved: Set[str] = set()
    remaining = list(nodes)
    
    current_level = 1
    while remaining:
        # Find all nodes whose dependencies have already been scheduled
        level_nodes = []
        for node in remaining:
            if all(dep in resolved for dep in node.dependencies):
                level_nodes.append(node)
                
        if not level_nodes:
            # Fallback for unexpected dependency deadlock/cycles
            for node in remaining:
                node.parallel_group = current_level
                node.stage_number = current_level
                resolved.add(node.id)
            break
            
        for node in level_nodes:
            node.parallel_group = current_level
            node.stage_number = current_level
            resolved.add(node.id)
            remaining.remove(node)
            
        current_level += 1
