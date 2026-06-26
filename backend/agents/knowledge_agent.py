from rag.llm import generate_answer


def run(context, question=None, conversation_history=None):
    """
    Executes the knowledge generation step.
    Supports ExecutionContext and backward compatible positional parameters.
    """
    if hasattr(context, 'question'):
        ctx = context
        context_str = "\n\n".join(ctx.retrieved_documents)
        web_sum = getattr(ctx, 'web_summary', None)
        graph_res = getattr(ctx, 'graph_results', None)
        ans = generate_answer(
            context=context_str,
            question=ctx.question,
            conversation_history=ctx.conversation_history,
            web_summary=web_sum,
            context_obj=ctx,
            graph_results=graph_res
        )
        ctx.draft_answer = ans
        return ans
    else:
        return generate_answer(
            context=context,
            question=question,
            conversation_history=conversation_history
        )