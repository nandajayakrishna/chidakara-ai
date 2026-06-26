from agents.planner_agent import plan
from agents.knowledge_agent import run as run_knowledge
from agents.critic_agent import review as run_critic
from agents.memory_agent import get_conversation_history, add_to_memory
from agents.tool_agent import run_tools
from agents.researcher_agent import gather
from agents.web_agent import run_web
from agents.graph_agent import run_graph
from agents.reflection_agent import run_reflection

# Define memory runner for sequential workflow execution
def run_memory(context_or_question, answer=None):
    if hasattr(context_or_question, 'question'):
        ctx = context_or_question
        workspace_id = getattr(ctx, "workspace_id", "default")
        loaded_turns = len(ctx.conversation_history) if ctx.conversation_history else 0
        ans = ctx.final_answer or ctx.draft_answer
        if not ans and ctx.tool_outputs:
            # Standard format for math/tool outputs
            ans = str(ctx.tool_outputs)
        add_to_memory(ctx.question, ans, workspace_id=workspace_id)
        stored_turns = len(get_conversation_history(workspace_id=workspace_id))
        ctx.debug_metadata["memory"] = {
            "turns_loaded": loaded_turns,
            "turns_stored": stored_turns
        }
    else:
        add_to_memory(context_or_question, answer)

# Registry mapping agent identifiers to their respective entrypoint functions.
# New agents can be registered here to extend the orchestrator with ease.
AGENT_REGISTRY = {
    "planner": plan,
    "research": gather,
    "knowledge": run_knowledge,
    "critic": run_critic,
    "tool": run_tools,
    "memory": run_memory,
    "web": run_web,
    "graph": run_graph,
    "reflection": run_reflection,
}


def get_agent(name):
    """
    Dynamically retrieve an agent by name from the registry.
    """
    return AGENT_REGISTRY.get(name)


def execute(context_or_question, context_str=None):
    """
    Sequentially executes the workflow steps resolved from the planner.
    Accumulates outputs in ExecutionContext and records chronological execution traces.
    """
    # 1. Initialize ExecutionContext if string values are passed (backward compatible mode)
    if hasattr(context_or_question, 'question'):
        ctx = context_or_question
    else:
        from agents.context import ExecutionContext
        ctx = ExecutionContext(
            question=context_or_question,
            conversation_history=get_conversation_history()
        )
        if context_str:
            ctx.retrieved_documents = [context_str]

    # 2. Determine ordered workflow steps
    planner = get_agent("planner")
    workflow = planner(ctx.question)
    ctx.workflow_state["workflow"] = workflow

    # Human-readable agent mapping
    agent_names = {
        "research": "Research Agent",
        "knowledge": "Knowledge Agent",
        "critic": "Critic Agent",
        "tool": "Tool Agent",
        "memory": "Memory Agent",
        "web": "Web Agent",
        "graph": "Graph Agent",
        "reflection": "Reflection Agent",
    }

    # 2. Determine ordered workflow steps or execution plan
    # Check if the planner returned a list (simple query) or ExecutionPlan dict
    if isinstance(workflow, list):
        plan_dict = {
            "goal": ctx.question,
            "tasks": [
                {
                    "task_id": "task_1",
                    "task_name": "Process Request",
                    "description": ctx.question,
                    "agent_workflow": workflow,
                    "dependencies": [],
                    "priority": 1,
                    "status": "pending",
                    "result": "",
                    "duration": 0.0
                }
            ],
            "status": "pending",
            "current_task_id": "",
            "completed_steps": []
        }
        original_workflow_list = workflow
    else:
        plan_dict = workflow
        original_workflow_list = [t["task_name"] for t in plan_dict.get("tasks", [])]

    ctx.workflow_state["workflow"] = plan_dict.get("tasks", [])[0]["agent_workflow"] if plan_dict.get("tasks") else []
    ctx.execution_plan = plan_dict
    ctx.plan_status = "running"
    
    # Track tasks
    tasks = plan_dict.get("tasks", [])
    ctx.remaining_tasks = [t["task_name"] for t in tasks]
    ctx.completed_tasks = []
    
    used_agents = ["Planner Agent"]
    memory_executed = False
    
    import time
    from workflow.workflow_executor import execute_workflow
    
    for task in tasks:
        task_id = task["task_id"]
        task_name = task["task_name"]
        
        ctx.current_task = task_name
        plan_dict["current_task_id"] = task_id
        
        # Remove from remaining list under lock
        with ctx._lock:
            if task_name in ctx.remaining_tasks:
                ctx._remaining_tasks.remove(task_name)
                
        task["status"] = "running"
        
        # Save original details
        original_question = ctx.question
        ctx.question = task["description"]
        
        # Reset intermediate states for task execution
        ctx.draft_answer = ""
        ctx.final_answer = ""
        
        # Skip research database query if documents were already provided via old parameters signature
        if "research" in task["agent_workflow"] and context_str and ctx.retrieved_documents:
            ctx.workflow_state["research_bypassed"] = True
            
        start_task_time = time.time()
        
        # Run subtask workflow executor
        execute_workflow(task["agent_workflow"], AGENT_REGISTRY, agent_names, ctx)
        
        task_duration = (time.time() - start_task_time) * 1000.0
        
        task_result = ctx.final_answer or ctx.draft_answer or str(ctx.tool_outputs)
        task["status"] = "completed"
        task["result"] = task_result
        task["duration"] = task_duration
        
        # Update completed tasks
        ctx.completed_tasks.append(task_name)
        
        # Restore original question
        ctx.question = original_question
        
        # Save task result to conversation history so next tasks can use it
        ctx.conversation_history.append((f"Completed Subtask: {task_name}", task_result))
        
        # Gather agents used
        for step in task["agent_workflow"]:
            used_agents.append(agent_names.get(step, f"{step.capitalize()} Agent"))
            if step == "memory":
                memory_executed = True

    # 4. Ensure short-term memory remains updated exactly as before
    if not memory_executed:
        run_memory(ctx)

    # 5. Populate, serialize and return response structure
    # Final answer is the result of the last task in the plan
    ans = tasks[-1]["result"] if tasks else "No tasks processed."
    ctx.final_answer = ans
    ctx.plan_status = "completed"
    ctx.execution_plan = plan_dict
    
    ctx.workflow_state["used_agents"] = used_agents

    from debug.trace_serializer import serialize_trace
    from debug.trace_builder import save_trace
    
    serialized = serialize_trace(ctx)
    save_trace(serialized)

    return {
        "answer": ans,
        "agents": used_agents,
        "workflow": original_workflow_list,
        "execution_trace": ctx.execution_trace,
        "trace": ctx.trace,
        "confidence_score": ctx.confidence_score,
        "confidence_reason": ctx.confidence_reason,
        "reflection_summary": ctx.reflection,
        "execution_plan": plan_dict,
        "plan_status": ctx.plan_status,
        "current_task": ctx.current_task,
        "completed_tasks": list(ctx.completed_tasks),
        "remaining_tasks": list(ctx.remaining_tasks),
        "parallel_metrics": ctx.debug_metadata.get("parallel_metrics", {})
    }


def get_step_input_summary(step: str, ctx) -> str:
    if step == "research":
        return f"Question: {ctx.question}"
    elif step == "graph":
        doc_count = len(ctx.retrieved_documents)
        return f"Retrieved documents: {doc_count}, Question: {ctx.question}"
    elif step == "knowledge":
        kb_count = len(ctx.retrieved_documents)
        web_present = bool(ctx.web_summary)
        return f"KB Chunks: {kb_count}, Web Summary Available: {web_present}"
    elif step == "web":
        return f"Query: {ctx.question}"
    elif step == "tool":
        return f"Query: {ctx.question}"
    elif step == "critic":
        return f"Draft Answer Length: {len(ctx.draft_answer) if ctx.draft_answer else 0}"
    elif step == "reflection":
        return f"Question: {ctx.question}, Draft Answer Length: {len(ctx.draft_answer) if ctx.draft_answer else 0}"
    elif step == "memory":
        ans = ctx.final_answer or ctx.draft_answer or str(ctx.tool_outputs)
        return f"Question: {ctx.question}, Answer Length: {len(ans) if ans else 0}"
    return ""


def get_step_output_summary(step: str, ctx, status: str) -> str:
    if status == "failed":
        return "Execution failed"
    if step == "research":
        return f"Retrieved {len(ctx.retrieved_documents)} document chunks"
    elif step == "graph":
        nodes_len = len(ctx.graph_nodes) if getattr(ctx, "graph_nodes", None) else 0
        edges_len = len(ctx.graph_edges) if getattr(ctx, "graph_edges", None) else 0
        return f"Nodes created: {nodes_len}, Edges created: {edges_len}"
    elif step == "knowledge":
        return f"Draft Answer Length: {len(ctx.draft_answer) if ctx.draft_answer else 0}"
    elif step == "web":
        return f"Web Summary Length: {len(ctx.web_summary) if ctx.web_summary else 0}"
    elif step == "tool":
        return f"Tool Outputs Keys: {list(ctx.tool_outputs.keys())}"
    elif step == "critic":
        return f"Final Answer Length: {len(ctx.final_answer) if ctx.final_answer else 0}"
    elif step == "reflection":
        ans_status = "Answered" if ctx.reflection.get("answered") else "Unanswered"
        halluc_status = "Hallucination Detected" if ctx.reflection.get("hallucination_detected") else "Clean"
        return f"Status: {ans_status}, Check: {halluc_status}, Confidence: {ctx.confidence_score}"
    elif step == "memory":
        return "Stored interaction to memory"
    return ""