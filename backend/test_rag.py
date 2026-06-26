from rag.rag_pipeline import ask_question

question = "Who is Nanda Jaya Krishna?"

answer = ask_question(question)

print("\n")
print("=" * 50)
print("ANSWER")
print("=" * 50)
print(answer)