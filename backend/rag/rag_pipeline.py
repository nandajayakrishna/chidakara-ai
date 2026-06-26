from agents.context import ExecutionContext
from agents.orchestrator import execute
from agents.memory_agent import get_conversation_history


def ask_question(question, workspace_id="default"):
    # Retrieve current short-term conversation memory history
    conversation_history = get_conversation_history(workspace_id=workspace_id)

    # Create ExecutionContext
    ctx = ExecutionContext(
        question=question,
        conversation_history=conversation_history
    )
    ctx.workspace_id = workspace_id

    # Delegate execution to Orchestrator workflow engine
    result = execute(ctx)

    # Attach sources accumulated in context to output
    result["sources"] = ctx.metadata

    return result