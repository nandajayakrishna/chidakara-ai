from rag.loader import load_pdf


pdf_path = "uploads/sample.pdf"

content = load_pdf(pdf_path)

print("\n")
print("=" * 50)
print("PDF CONTENT")
print("=" * 50)
print(content[:2000])