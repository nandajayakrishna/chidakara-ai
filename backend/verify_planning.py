import sys
import time
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

from rag.rag_pipeline import ask_question

# Mocking Gemini LLM calls exactly as before to make it deterministic and rate-limit free
class MockResponse:
    def __init__(self, text):
        self.text = text

def mock_generate_content(prompt):
    prompt_lower = prompt.lower()
    
    # 1. Entity Extraction
    if "you are an entity extraction agent" in prompt_lower:
        return MockResponse(
            '[{"name": "Python", "type": "Programming Language"}, {"name": "B.Tech", "type": "Project"}]'
        )
    # 2. Relationship Extraction
    elif "you are a relationship extraction agent" in prompt_lower:
        return MockResponse(
            '[{"subject": "B.Tech", "predicate": "uses", "object": "Python"}]'
        )
    # 3. Graph Search
    elif "you are a graph search agent" in prompt_lower:
        return MockResponse("My publication uses CNN for Brain Tumor Detection.")
    # 4. Web Search / Web Intelligence Agent
    elif "you are a web search agent" in prompt_lower or "you are a web intelligence agent" in prompt_lower:
        return MockResponse("The latest CNN papers focus on Transformer hybrid models.")
    # 5. Reflection Agent
    elif "you are a reflection agent" in prompt_lower:
        return MockResponse(
            '{"answered": true, "missing_information": [], "hallucination_detected": false, "confidence": 0.95, "reason": "Answer fully supported."}'
        )
    # 6. Critic Agent
    elif "you are a critic agent" in prompt_lower:
        if "nvidia" in prompt_lower:
            return MockResponse("Here is your NVIDIA Hackathon implementation roadmap.")
        elif "rust" in prompt_lower:
            return MockResponse("Here is your Python vs Rust comparative summary.")
        elif "publication" in prompt_lower:
            return MockResponse("Here is the CNN comparative summary.")
        else:
            return MockResponse("Your CGPA is 7.12.")
    # 7. Knowledge Agent / LLM
    elif "you are chidakara knowledge assistant" in prompt_lower:
        if "nvidia" in prompt_lower:
            return MockResponse("NVIDIA Hackathon roadmap details.")
        elif "rust" in prompt_lower:
            return MockResponse("Python vs Rust comparative summary details.")
        elif "publication" in prompt_lower:
            return MockResponse("CNN comparative summary details.")
        else:
            return MockResponse("Your CGPA is 7.12.")

    return MockResponse("Mock default response.")

import rag.llm_client
rag.llm_client.model.generate_content = mock_generate_content

def run_tests():
    print("=" * 60)
    print("RUNNING AUTOMATED PLANNER & GOAL DECOMPOSITION VERIFICATION")
    print("=" * 60)

    # Test 1: "What is my CGPA?" -> Single task
    print("\n--- Test 1: Simple Query ('What is my CGPA?') ---")
    res1 = ask_question("What is my CGPA?")
    print(f"Answer: {res1['answer']}")
    print(f"Plan Tasks: {[t['task_name'] for t in res1['execution_plan']['tasks']]}")
    print(f"Plan Status: {res1['plan_status']}")
    assert len(res1['execution_plan']['tasks']) == 1, "Expected single task plan"
    assert res1['execution_plan']['tasks'][0]['task_name'] == "Process Request"
    print("Test 1 Passed: Simple query returned single task plan.")

    # Test 2: "Summarize my resume." -> Single task
    print("\n--- Test 2: Simple Query ('Summarize my resume.') ---")
    res2 = ask_question("Summarize my resume.")
    print(f"Answer: {res2['answer']}")
    print(f"Plan Tasks: {[t['task_name'] for t in res2['execution_plan']['tasks']]}")
    print(f"Plan Status: {res2['plan_status']}")
    assert len(res2['execution_plan']['tasks']) == 1, "Expected single task plan"
    print("Test 2 Passed: Resume query returned single task plan.")

    # Test 3: "Help me prepare for NVIDIA Hackathon." -> Multi-task plan
    print("\n--- Test 3: Multi-task Query ('Help me prepare for NVIDIA Hackathon.') ---")
    res3 = ask_question("Help me prepare for NVIDIA Hackathon.")
    print(f"Answer: {res3['answer']}")
    tasks3 = [t['task_name'] for t in res3['execution_plan']['tasks']]
    print(f"Plan Tasks: {tasks3}")
    print(f"Plan Status: {res3['plan_status']}")
    assert len(res3['execution_plan']['tasks']) > 1, "Expected multi-task plan"
    assert "Understand project" in tasks3
    assert "Produce implementation roadmap" in tasks3
    print("Test 3 Passed: Multi-task Nvidia query returned correct decomposed subtasks.")

    # Test 4: "Research Python, compare with Rust, then summarize." -> Multi-task plan
    print("\n--- Test 4: Multi-task Query ('Research Python, compare with Rust, then summarize.') ---")
    res4 = ask_question("Research Python, compare with Rust, then summarize.")
    print(f"Answer: {res4['answer']}")
    tasks4 = [t['task_name'] for t in res4['execution_plan']['tasks']]
    print(f"Plan Tasks: {tasks4}")
    print(f"Plan Status: {res4['plan_status']}")
    assert len(res4['execution_plan']['tasks']) > 1, "Expected multi-task plan"
    assert "Research Python" in tasks4
    assert "Compare Python and Rust" in tasks4
    print("Test 4 Passed: Multi-task comparison query returned correct decomposed subtasks.")

    # Test 5: "My publication, latest CNN papers and compare them." -> Mixed Graph + Web + Knowledge plan
    print("\n--- Test 5: Mixed Query ('My publication, latest CNN papers and compare them.') ---")
    res5 = ask_question("My publication, latest CNN papers and compare them.")
    print(f"Answer: {res5['answer']}")
    tasks5 = [t['task_name'] for t in res5['execution_plan']['tasks']]
    print(f"Plan Tasks: {tasks5}")
    print(f"Plan Status: {res5['plan_status']}")
    assert len(res5['execution_plan']['tasks']) > 1, "Expected multi-task plan"
    assert "Analyze my publication" in tasks5
    assert "Search latest CNN papers" in tasks5
    
    # Check that task 1 contains graph step
    t1 = res5['execution_plan']['tasks'][0]
    assert "graph" in t1['agent_workflow'], "Expected graph agent in first subtask workflow"
    
    # Check that task 2 contains web step
    t2 = res5['execution_plan']['tasks'][1]
    assert "web" in t2['agent_workflow'], "Expected web agent in second subtask workflow"
    
    print("Test 5 Passed: Mixed query successfully mapped Graph + Web subtasks.")

    print("\n" + "=" * 60)
    print("ALL PLANNER VALIDATION TESTS PASSED SUCCESSFULLY! (OK)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_tests()
        sys.exit(0)
    except AssertionError as ae:
        print(f"\nASSERTION FAILED: {str(ae)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED FAILURE: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
