import time
from datetime import datetime
from typing import Dict, Any, List
from workflow.dependency_analyzer import analyze_dependencies
from workflow.parallel_runner import run_parallel_stage
from workflow.workflow_graph import WorkflowDAG

def execute_workflow(steps: List[str], agent_registry: Dict[str, Any], agent_names: Dict[str, str], ctx) -> Dict[str, Any]:
    """
    Executes the workflow graph concurrently, resolves metrics, and populates the ExecutionContext.
    """
    # 1. Analyze dependencies & Schedule levels
    dag = analyze_dependencies(steps, agent_registry)
    
    # Store parallel metadata in context for access during node execution
    node_groups = {node.id: node.parallel_group for node in dag.get_all_nodes()}
    dependencies = {node.id: node.dependencies for node in dag.get_all_nodes()}
    
    ctx.workflow_state["node_groups"] = node_groups
    ctx.workflow_state["dependencies"] = dependencies
    
    # 2. Partition nodes into sequential stage levels
    max_level = max([node.parallel_group for node in dag.get_all_nodes()]) if dag.get_all_nodes() else 1
    stages: Dict[int, List[any]] = {i: [] for i in range(1, max_level + 1)}
    
    for node in dag.get_all_nodes():
        stages[node.parallel_group].append(node)

    # 3. Synchronous loop over stages, parallel execution within stages
    start_wall_time = time.time()
    
    # Intercept agent callables to run worker wrappers (measuring latency and logging execution traces)
    for node in dag.get_all_nodes():
        node.callable = make_trace_worker(node.id, node.callable, agent_names)
        
    for level in range(1, max_level + 1):
        stage_nodes = stages[level]
        run_parallel_stage(stage_nodes, ctx)
        
    end_wall_time = time.time()
    total_execution_time = (end_wall_time - start_wall_time) * 1000.0

    # 4. Post-Execution Metrics & Critical Path Calculation
    metrics = compute_parallel_metrics(dag, total_execution_time)
    
    with ctx._lock:
        ctx.debug_metadata["parallel_metrics"] = metrics
        
    return metrics

def make_trace_worker(step_id: str, original_callable: any, agent_names: Dict[str, str]):
    """
    Wraps the agent callable to format inputs, outputs, and log step traces to context.
    """
    from agents.orchestrator import get_step_input_summary, get_step_output_summary
    
    def worker(ctx):
        agent_name = agent_names.get(step_id, f"{step_id.capitalize()} Agent")
        
        # Guard for bypassed research database query (e.g. if documents passed in old API signature)
        if step_id == "research" and ctx.workflow_state.get("research_bypassed", False):
            now_iso = datetime.utcnow().isoformat() + "Z"
            with ctx._lock:
                ctx.execution_trace.append({
                    "step": step_id,
                    "agent": agent_name,
                    "status": "completed",
                    "timestamp": now_iso,
                    "step_id": step_id,
                    "agent_name": agent_name,
                    "start_time": now_iso,
                    "end_time": now_iso,
                    "duration_ms": 0.0,
                    "input_summary": "Retrieved documents passed as string signature parameter",
                    "output_summary": f"Using {len(ctx.retrieved_documents)} pre-provided documents",
                    "error": None,
                    "debug_metadata": {"bypassed": True},
                    "parallel_group": 1,
                    "dependency_chain": [],
                    "stage_number": 1
                })
            return

        start_time_iso = datetime.utcnow().isoformat() + "Z"
        start_time_s = time.time()
        
        status = "completed"
        error_str = None
        input_summary = get_step_input_summary(step_id, ctx)
        
        try:
            retries_attempted = 0
            while True:
                try:
                    original_callable(ctx)
                    break
                except Exception as e:
                    if retries_attempted < 1:
                        retries_attempted += 1
                        with ctx._lock:
                            ctx.workflow_state["retry_count"] = ctx.workflow_state.get("retry_count", 0) + 1
                        continue
                    status = "failed"
                    error_str = str(e)
                    with ctx._lock:
                        ctx.workflow_state["failed"] = True
                    raise e
        finally:
            end_time_iso = datetime.utcnow().isoformat() + "Z"
            duration_ms = (time.time() - start_time_s) * 1000.0
            output_summary = get_step_output_summary(step_id, ctx, status)
            
            with ctx._lock:
                ctx.execution_trace.append({
                    "step": step_id,
                    "agent": agent_name,
                    "status": status,
                    "timestamp": end_time_iso,
                    "step_id": step_id,
                    "agent_name": agent_name,
                    "start_time": start_time_iso,
                    "end_time": end_time_iso,
                    "duration_ms": duration_ms,
                    "input_summary": input_summary,
                    "output_summary": output_summary,
                    "error": error_str,
                    "debug_metadata": dict(ctx.debug_metadata.get(step_id, {})),
                    "parallel_group": ctx.workflow_state.get("node_groups", {}).get(step_id, 1),
                    "dependency_chain": ctx.workflow_state.get("dependencies", {}).get(step_id, []),
                    "stage_number": ctx.workflow_state.get("node_groups", {}).get(step_id, 1)
                })
    return worker

def compute_parallel_metrics(dag: WorkflowDAG, total_execution_time_ms: float) -> Dict[str, Any]:
    """
    Computes critical path, agent utilization, parallel efficiency, and idle times.
    """
    nodes = dag.get_all_nodes()
    sum_durations_ms = sum(node.duration for node in nodes)
    
    # Compute maximum parallelism (largest stage count)
    stages_count = {}
    for node in nodes:
        stages_count[node.parallel_group] = stages_count.get(node.parallel_group, 0) + 1
    max_parallelism = max(stages_count.values()) if stages_count else 1

    # Find critical path dynamically using dynamic programming on DAG:
    dist = {}
    prev = {}
    
    # Sort topologically
    topo_sorted = sorted(nodes, key=lambda n: n.parallel_group)
    
    for node in topo_sorted:
        max_dep_dist = 0.0
        best_dep = None
        for dep_id in node.dependencies:
            dep_dist = dist.get(dep_id, 0.0)
            if dep_dist > max_dep_dist:
                max_dep_dist = dep_dist
                best_dep = dep_id
        dist[node.id] = node.duration + max_dep_dist
        prev[node.id] = best_dep
        
    critical_path_nodes = []
    if nodes:
        end_node_id = max(dist.keys(), key=lambda k: dist[k])
        critical_path_time_ms = dist[end_node_id]
        
        curr = end_node_id
        while curr is not None:
            critical_path_nodes.insert(0, curr)
            curr = prev.get(curr)
    else:
        critical_path_time_ms = 0.0
        
    # Parallel efficiency: Sum of node durations / (Total execution time * Max Parallelism)
    if total_execution_time_ms > 0:
        parallel_efficiency = min(1.0, sum_durations_ms / (total_execution_time_ms * max_parallelism))
        idle_time_ms = max(0.0, (max_parallelism * total_execution_time_ms) - sum_durations_ms)
    else:
        parallel_efficiency = 1.0
        idle_time_ms = 0.0
        
    # Agent utilization ratio
    agent_utilization = {}
    for node in nodes:
        agent_utilization[node.id] = round(node.duration / total_execution_time_ms, 4) if total_execution_time_ms > 0 else 1.0

    return {
        "total_execution_time_ms": round(total_execution_time_ms, 2),
        "critical_path_time_ms": round(critical_path_time_ms, 2),
        "critical_path": critical_path_nodes,
        "parallel_efficiency": round(parallel_efficiency, 4),
        "idle_time_ms": round(idle_time_ms, 2),
        "maximum_parallelism": max_parallelism,
        "agent_utilization": agent_utilization
    }
