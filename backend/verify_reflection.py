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

# Mock response class
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
        return MockResponse("Python is connected to B.Tech projects in the knowledge graph.")

    # 4. Web Search / Web Intelligence Agent
    elif "you are a web search agent" in prompt_lower or "you are a web intelligence agent" in prompt_lower:
        return MockResponse("OpenAI recently announced new API updates.")

    # 5. Reflection Agent
    elif "you are a reflection agent" in prompt_lower:
        if "what is my cgpa?" in prompt_lower:
            if "studied history" in prompt_lower or "9.99" in prompt_lower:
                # Test 6: Hallucination detection
                return MockResponse(
                    '{"answered": true, "missing_information": [], "hallucination_detected": true, "confidence": 0.30, "reason": "Draft answer states CGPA of 9.99 and studying history, which is not supported by the retrieved CGPA of 7.12."}'
                )
            else:
                # Test 1: Standard QA
                return MockResponse(
                    '{"answered": true, "missing_information": [], "hallucination_detected": false, "confidence": 0.95, "reason": "CGPA of 7.12 is fully supported by the document context."}'
                )
        elif "what is my favorite color?" in prompt_lower:
            # Test 2: Unknown query
            return MockResponse(
                '{"answered": false, "missing_information": ["Favorite color not in document"], "hallucination_detected": false, "confidence": 0.10, "reason": "No evidence regarding favorite color."}'
            )
        elif "latest news" in prompt_lower:
            # Test 3: Web query
            return MockResponse(
                '{"answered": true, "missing_information": [], "hallucination_detected": false, "confidence": 0.92, "reason": "News about OpenAI was answered using web results."}'
            )
        elif "projects" in prompt_lower:
            # Test 4: Graph query
            return MockResponse(
                '{"answered": true, "missing_information": [], "hallucination_detected": false, "confidence": 0.94, "reason": "Relationships resolved using graph node connections."}'
            )
        else:
            return MockResponse(
                '{"answered": false, "missing_information": [], "hallucination_detected": false, "confidence": 0.15, "reason": "Default fallback."}'
            )

    # 6. Critic Agent
    elif "you are a critic agent" in prompt_lower:
        if "what is my cgpa?" in prompt_lower:
            return MockResponse("Your CGPA is 7.12.")
        elif "what is my favorite color?" in prompt_lower:
            return MockResponse("I could not find that information in the knowledge base.")
        elif "latest news" in prompt_lower:
            return MockResponse("OpenAI has announced several new updates.")
        elif "python" in prompt_lower:
            return MockResponse("Python is connected to B.Tech projects.")
        else:
            return MockResponse("I could not find that information in the knowledge base.")

    # 7. Knowledge Agent / LLM
    elif "you are chidakara knowledge assistant" in prompt_lower:
        if "what is my cgpa?" in prompt_lower:
            return MockResponse("Your CGPA is 7.12.")
        elif "what is my favorite color?" in prompt_lower:
            return MockResponse("I could not find that information in the knowledge base.")
        elif "latest news" in prompt_lower:
            return MockResponse("OpenAI has announced several new updates.")
        elif "python" in prompt_lower:
            return MockResponse("Python is connected to B.Tech projects.")
        else:
            return MockResponse("I could not find that information in the knowledge base.")

    return MockResponse("Mock fallback response.")

# Apply the monkey-patch on the model instance
import rag.llm_client
rag.llm_client.model.generate_content = mock_generate_content

# Now import the test pipeline and context
from rag.rag_pipeline import ask_question
from agents.reflection_agent import run_reflection
from agents.context import ExecutionContext

def run_tests():
    print("=" * 60)
    print("RUNNING AUTOMATED REFLECTION & CONFIDENCE ENGINE VERIFICATION")
    print("=" * 60)

    # 1. Standard QA Query: "What is my CGPA?"
    print("\n--- Test 1: Standard QA Query ('What is my CGPA?') ---")
    res1 = ask_question("What is my CGPA?")
    print(f"Answer: {res1['answer']}")
    print(f"Confidence: {res1['confidence_score']}")
    print(f"Reason: {res1['confidence_reason']}")
    print(f"Workflow: {res1['workflow']}")
    assert res1['confidence_score'] > 0.90, f"Expected confidence > 0.90, got {res1['confidence_score']}"
    print("Test 1 Passed: Standard QA query returned >0.90 confidence.")

    # 2. Unknown Query: "What is my favorite color?"
    print("\n--- Test 2: Unknown Query ('What is my favorite color?') ---")
    res2 = ask_question("What is my favorite color?")
    print(f"Answer: {res2['answer']}")
    print(f"Confidence: {res2['confidence_score']}")
    print(f"Reason: {res2['confidence_reason']}")
    print(f"Workflow: {res2['workflow']}")
    assert res2['confidence_score'] < 0.40, f"Expected confidence < 0.40, got {res2['confidence_score']}"
    assert "I could not find that information" in res2['answer'] or "not find that information in the knowledge base" in res2['answer'], "Expected fallback response"
    print("Test 2 Passed: Unknown query returned <0.40 confidence and fallback response.")

    # 3. Web Query: "What is the latest news about OpenAI?" (triggers web query routing)
    print("\n--- Test 3: Web Query ('What is the latest news about OpenAI?') ---")
    res3 = ask_question("What is the latest news about OpenAI?")
    print(f"Answer: {res3['answer']}")
    print(f"Confidence: {res3['confidence_score']}")
    print(f"Reason: {res3['confidence_reason']}")
    print(f"Workflow: {res3['workflow']}")
    assert "web" in res3['workflow'], "Expected web agent in workflow"
    print("Test 3 Passed: Web query correctly executed Web Agent and computed confidence.")

    # 4. Graph Query: "What projects are connected to Python?" (triggers graph query routing)
    print("\n--- Test 4: Graph Query ('What projects are connected to Python?') ---")
    res4 = ask_question("What projects are connected to Python?")
    print(f"Answer: {res4['answer']}")
    print(f"Confidence: {res4['confidence_score']}")
    print(f"Reason: {res4['confidence_reason']}")
    print(f"Workflow: {res4['workflow']}")
    assert "graph" in res4['workflow'], "Expected graph agent in workflow"
    print("Test 4 Passed: Graph query correctly executed Graph Agent and computed confidence.")

    # 5. Tool Query: "Calculate 15 * (12 + 8)"
    print("\n--- Test 5: Tool Query ('Calculate 15 * (12 + 8)') ---")
    res5 = ask_question("Calculate 15 * (12 + 8)")
    print(f"Answer: {res5['answer']}")
    print(f"Confidence: {res5['confidence_score']}")
    print(f"Reason: {res5['confidence_reason']}")
    print(f"Workflow: {res5['workflow']}")
    assert "tool" in res5['workflow'], "Expected tool agent in workflow"
    assert res5['confidence_score'] == 1.0, f"Expected tool confidence = 1.0, got {res5['confidence_score']}"
    print("Test 5 Passed: Tool query returned exactly 1.0 confidence.")

    # 6. Reflection Agent Mismatched/Hallucinated Test
    print("\n--- Test 6: Reflection detects unsupported answers ---")
    ctx = ExecutionContext("What is my CGPA?")
    ctx.retrieved_documents = ["The candidate graduated with a CGPA of 7.12."]
    ctx.draft_answer = "The candidate has a CGPA of 9.99 and studied history." # Obvious hallucination
    
    res6 = run_reflection(ctx)
    print(f"Reflection Result: {res6}")
    print(f"Confidence Score: {ctx.confidence_score}")
    print(f"Confidence Reason: {ctx.confidence_reason}")
    assert res6['hallucination_detected'] == True, "Expected hallucination to be detected"
    assert ctx.confidence_score < 0.40, f"Expected confidence score < 0.40, got {ctx.confidence_score}"
    print("Test 6 Passed: Reflection agent successfully flagged hallucinated content.")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (OK)")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_tests()
        sys.exit(0)
    except AssertionError as ae:
        print(f"\nASSERTION FAILED: {str(ae)}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
