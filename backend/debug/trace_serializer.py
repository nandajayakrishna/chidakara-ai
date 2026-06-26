from datetime import datetime
from typing import Dict, Any

def serialize_trace(ctx) -> Dict[str, Any]:
    """
    Serializes ExecutionContext trace data and metadata into a JSON-compatible dictionary.
    """
    steps = []
    
    parallel_metrics = ctx.debug_metadata.get("parallel_metrics", {})
    critical_path = parallel_metrics.get("critical_path", [])
    
    for entry in ctx.execution_trace:
        step_id = entry.get("step")
        steps.append({
            "step_id": step_id,
            "agent_name": entry.get("agent"),
            "start_time": entry.get("start_time"),
            "end_time": entry.get("end_time"),
            "duration_ms": entry.get("duration_ms", 0.0),
            "status": entry.get("status"),
            "input_summary": entry.get("input_summary", ""),
            "output_summary": entry.get("output_summary", ""),
            "error": entry.get("error"),
            "debug_metadata": entry.get("debug_metadata", {}),
            # Parallel execution attributes
            "parallel_group": entry.get("parallel_group", 1),
            "dependency_chain": entry.get("dependency_chain", []),
            "critical_path": step_id in critical_path,
            "stage_number": entry.get("stage_number", 1)
        })
        
    workflow = ctx.workflow_state.get("workflow", [])
    
    # Identify skipped steps: steps present in workflow plan but not executed
    executed_steps = {s["step_id"] for s in steps}
    skipped_steps = [w for w in workflow if w not in executed_steps]
    
    # Accumulate total duration of step execution
    total_duration_ms = sum(s["duration_ms"] for s in steps)
    
    # Calculate success status
    success = all(s["status"] == "completed" for s in steps) if steps else True
    if ctx.workflow_state.get("failed", False):
        success = False
        
    return {
        "trace_id": ctx.trace_id,
        "question": ctx.question,
        "workflow": workflow,
        "success": success,
        "total_duration_ms": total_duration_ms,
        "skipped_steps": skipped_steps,
        "retry_count": ctx.workflow_state.get("retry_count", 0),
        "steps": steps,
        "confidence_score": getattr(ctx, "confidence_score", 0.0),
        "confidence_reason": getattr(ctx, "confidence_reason", ""),
        "reflection": getattr(ctx, "reflection", {}),
        "parallel_metrics": parallel_metrics,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        # Planning variables
        "execution_plan": getattr(ctx, "execution_plan", {}),
        "plan_status": getattr(ctx, "plan_status", "pending"),
        "current_task": getattr(ctx, "current_task", ""),
        "completed_tasks": list(getattr(ctx, "completed_tasks", [])),
        "remaining_tasks": list(getattr(ctx, "remaining_tasks", []))
    }
