import sys
import time
import threading
from unittest.mock import MagicMock

# Mock sentence_transformers and chromadb before any other imports to prevent MemoryError
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['chromadb'] = MagicMock()

import rag.embedder
import rag.retriever

rag.embedder.create_embeddings = lambda chunks: [[0.1] * 384 for _ in chunks]
rag.retriever.search = lambda query_embedding, n_results=8: {
    "documents": ["The candidate graduated with a CGPA of 7.12.", "Details of B.Tech project in Python."],
    "metadata": [{"source": "resume.pdf"}, {"source": "projects.pdf"}],
    "distances": [0.1, 0.2]
}

# Define Mock Responses with simulated network latency
class MockResponse:
    def __init__(self, text):
        self.text = text

def mock_generate_content(prompt):
    # Simulate API network latency of 150ms
    time.sleep(0.15)
    
    prompt_lower = prompt.lower()
    if "you are an entity extraction agent" in prompt_lower:
        return MockResponse(
            '[{"name": "Python", "type": "Programming Language"}, {"name": "B.Tech", "type": "Project"}]'
        )
    elif "you are a relationship extraction agent" in prompt_lower:
        return MockResponse(
            '[{"subject": "B.Tech", "predicate": "uses", "object": "Python"}]'
        )
    elif "you are a graph search agent" in prompt_lower:
        return MockResponse("Python is connected to B.Tech projects in the knowledge graph.")
    elif "you are a web search agent" in prompt_lower or "you are a web intelligence agent" in prompt_lower:
        return MockResponse("OpenAI recently announced new API updates.")
    elif "you are a reflection agent" in prompt_lower:
        return MockResponse(
            '{"answered": true, "missing_information": [], "hallucination_detected": false, "confidence": 0.95, "reason": "Answer fully supported by context."}'
        )
    elif "you are a critic agent" in prompt_lower:
        return MockResponse("Python is connected to B.Tech projects.")
    elif "you are chidakara knowledge assistant" in prompt_lower:
        return MockResponse("Python is connected to B.Tech projects.")
        
    return MockResponse("Mock default response.")

# Patch LLM client
import rag.llm_client
rag.llm_client.model.generate_content = mock_generate_content

# Now import context and pipelines
from agents.context import ExecutionContext
from rag.rag_pipeline import ask_question
from agents.orchestrator import execute, AGENT_REGISTRY, get_conversation_history

def test_thread_safety():
    print("\n--- Test 1: Thread Safety Verification ---")
    ctx = ExecutionContext("dummy")
    
    def worker(thread_id):
        for i in range(50):
            # Concurrent dictionary updates
            ctx.debug_metadata[f"thread_{thread_id}_key_{i}"] = i
            ctx.tool_outputs[f"thread_{thread_id}_tool_{i}"] = f"val_{i}"
            # Concurrent list updates
            ctx.retrieved_documents.append(f"doc_{thread_id}_{i}")
            
    threads = [threading.Thread(target=worker, args=(t,)) for t in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
        
    assert len(ctx.retrieved_documents) == 500, f"Expected 500 items, got {len(ctx.retrieved_documents)}"
    assert len(ctx.debug_metadata.keys()) == 500, f"Expected 500 keys in debug_metadata, got {len(ctx.debug_metadata.keys())}"
    print("Test 1 Passed: ThreadSafeDict and ThreadSafeList operated safely under concurrent loads.")

def test_dependency_ordering(execution_trace):
    print("\n--- Test 2: Dependency Ordering Verification ---")
    
    # Extract step execution times
    times = {t["step"]: (t["start_time"], t["end_time"]) for t in execution_trace}
    
    # Assert Knowledge runs after dependency steps
    if "knowledge" in times:
        k_start = times["knowledge"][0]
        for dep in ["research", "graph", "web"]:
            if dep in times:
                dep_end = times[dep][1]
                assert k_start >= dep_end, f"Dependency ordering failure: Knowledge started before {dep} completed."
                
    # Assert Reflection runs after Knowledge
    if "reflection" in times and "knowledge" in times:
        r_start = times["reflection"][0]
        k_end = times["knowledge"][1]
        assert r_start >= k_end, "Dependency ordering failure: Reflection started before Knowledge completed."
        
    # Assert Critic runs after Reflection
    if "critic" in times and "reflection" in times:
        c_start = times["critic"][0]
        ref_end = times["reflection"][1]
        assert c_start >= ref_end, "Dependency ordering failure: Critic started before Reflection completed."
        
    print("Test 2 Passed: Topological graph dependency scheduling is verified.")

def test_metrics_integrity(parallel_metrics):
    print("\n--- Test 3: Metrics Integrity Verification ---")
    assert "total_execution_time_ms" in parallel_metrics
    assert "critical_path_time_ms" in parallel_metrics
    assert "critical_path" in parallel_metrics
    assert "parallel_efficiency" in parallel_metrics
    assert "maximum_parallelism" in parallel_metrics
    assert "agent_utilization" in parallel_metrics
    
    efficiency = parallel_metrics["parallel_efficiency"]
    assert 0.0 <= efficiency <= 1.0, f"Expected parallel efficiency in [0..1], got {efficiency}"
    print(f"Parallel Efficiency: {efficiency}")
    print(f"Critical Path: {parallel_metrics['critical_path']}")
    print("Test 3 Passed: Concurrency metrics and critical path parsed successfully.")

def run_sequential_simulation(question):
    """
    Simulates the old sequential workflow execution.
    """
    from agents.planner_agent import plan
    from agents.memory_agent import get_conversation_history
    
    ctx = ExecutionContext(
        question=question,
        conversation_history=get_conversation_history()
    )
    workflow = plan(ctx.question)
    
    # Deduplicate steps sequentially
    seen = set()
    unique_steps = []
    for step in workflow:
        if step not in seen and step in AGENT_REGISTRY:
            seen.add(step)
            unique_steps.append(step)
            
    start_time = time.time()
    for step in unique_steps:
        # Run agent
        agent = AGENT_REGISTRY[step]
        agent(ctx)
    end_time = time.time()
    
    return ctx, (end_time - start_time) * 1000.0

def run_tests_and_benchmarks():
    # Run thread-safety checks first
    test_thread_safety()
    
    # Run benchmark query
    query = "What projects are connected to Python?"
    print(f"\n--- Running Benchmark Query: '{query}' ---")
    
    # 1. Parallel execution (new engine default ask_question)
    start_parallel = time.time()
    res_parallel = ask_question(query)
    parallel_duration_ms = (time.time() - start_parallel) * 1000.0
    
    # 2. Sequential execution
    ctx_seq, sequential_duration_ms = run_sequential_simulation(query)
    
    print(f"\nSequential Duration: {sequential_duration_ms:.2f} ms")
    print(f"Parallel Duration (Wall Clock): {parallel_duration_ms:.2f} ms")
    
    # 3. Output Correctness
    assert res_parallel["answer"] == ctx_seq.final_answer, f"Outputs differ!\nParallel: {res_parallel['answer']}\nSequential: {ctx_seq.final_answer}"
    print("\nCorrectness Verified: Sequential and Parallel engines returned identical answers.")
    
    # 4. Dependency & Metrics Checks
    test_dependency_ordering(res_parallel["execution_trace"])
    
    parallel_metrics = res_parallel["parallel_metrics"]
    test_metrics_integrity(parallel_metrics)
    
    # 5. Performance Report
    speedup = sequential_duration_ms / parallel_duration_ms
    latency_reduction = ((sequential_duration_ms - parallel_duration_ms) / sequential_duration_ms) * 100.0
    
    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARK RESULTS")
    print("=" * 60)
    print(f"Sequential Execution Time: {sequential_duration_ms:.2f} ms")
    print(f"Parallel Execution Time:   {parallel_duration_ms:.2f} ms")
    print(f"Execution Speedup:         {speedup:.2f}x")
    print(f"Latency Reduction:         {latency_reduction:.2f}%")
    print(f"Parallel Efficiency:       {parallel_metrics['parallel_efficiency'] * 100.0:.2f}%")
    print(f"Maximum Parallelism:       {parallel_metrics['maximum_parallelism']}")
    print(f"Critical Path Time:        {parallel_metrics['critical_path_time_ms']:.2f} ms")
    print(f"Critical Path:             { ' -> '.join(parallel_metrics['critical_path']) }")
    print("=" * 60)
    print("ALL CONCURRENCY TESTS PASSED SUCCESSFULLY! (OK)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_tests_and_benchmarks()
        sys.exit(0)
    except AssertionError as ae:
        print(f"\nASSERTION FAILED: {str(ae)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
