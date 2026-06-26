from agents.tool_agent import is_math_query, is_date_time_query, is_json_query, is_text_stats_query
from planning.goal_parser import classify_goal
from planning.task_decomposer import decompose_goal

def plan(question_or_ctx):
    if hasattr(question_or_ctx, 'question'):
        question = question_or_ctx.question
    else:
        question = question_or_ctx
        
    # Detect if query requires autonomous multi-task planning
    classification = classify_goal(question)
    if classification == "multi_step":
        plan_obj = decompose_goal(question)
        return plan_obj.to_dict()

    q = question.lower()

    # Detect external web query indicators
    web_keywords = [
        "latest", "today", "current", "recent", "news", "price",
        "weather", "stock", "nvidia", "openai", "github",
        "release", "version", "announcement"
    ]
    has_web_indicator = any(word in q for word in web_keywords)

    # Detect graph connection indicators
    graph_keywords = [
        "connected", "relation", "relationship", "projects use", "project uses",
        "publication uses", "publication is related", "skills are related", "skills were used",
        "associated with", "technologies are connected", "connected to"
    ]
    has_graph_indicator = any(word in q for word in graph_keywords)

    # Detect RAG indicators
    has_rag_indicator = any(
        word in q
        for word in [
            "summarize", "analyse", "analyze", "compare", 
            "evaluate", "report", "insights", "cgpa", "resume"
        ]
    )
    # Detect Tool indicators
    has_tool_indicator = any(
        word in q
        for word in ["count", "statistic", "word", "character", "line"]
    )

    # 1. Graph queries
    if has_graph_indicator:
        return ["research", "graph", "knowledge", "reflection", "critic"]

    # 2. Combined RAG + Web search query
    if has_rag_indicator and has_web_indicator:
        return ["research", "knowledge", "web", "knowledge", "reflection", "critic"]

    # 2. Combined RAG + Tool query (e.g., summarize resume AND count words/statistics)
    if has_rag_indicator and has_tool_indicator:
        return ["research", "knowledge", "tool", "reflection", "critic"]

    # 3. Pure external web query
    if has_web_indicator:
        return ["web", "knowledge", "reflection", "critic"]

    # 4. Publication-specific query triggering conversational memory flow
    if "publication" in q:
        return ["research", "knowledge", "memory", "reflection", "critic"]

    # 3. Pure tool query
    if is_math_query(question) or is_date_time_query(question) or is_json_query(question) or is_text_stats_query(question):
        return ["tool", "reflection", "critic"]

    # 4. Standard QA or Analysis queries
    return ["research", "knowledge", "reflection", "critic"]