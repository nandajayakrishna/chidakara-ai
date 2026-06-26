def classify_goal(prompt: str) -> str:
    """
    Classifies a user prompt into:
    - 'simple_query': Single fact lookup or direct prompt (e.g. "What is my CGPA?", "Summarize my resume")
    - 'multi_step': Planning request, multi-step goal, or project outline query.
    """
    q = prompt.lower()
    
    # Keyword indicators that warrant task decomposition and multi-step execution plans
    multi_indicators = [
        "prepare for", "roadmap", "plan to", "how do i build", "how to build", 
        "project outline", "implementation plan", "research, compare, then",
        "then compare", "then summarize", "and compare them", "step by step",
        "hackathon", "develop a", "design a", "compare with", "then"
    ]
    
    if any(ind in q for ind in multi_indicators):
        return "multi_step"
        
    return "simple_query"
