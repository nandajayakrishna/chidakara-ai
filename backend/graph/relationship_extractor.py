import json
from typing import List, Dict, Any
from rag.llm_client import model

def extract_relationships(text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extracts semantic relationships between entities from text using the Gemini LLM.
    Returns a list of triples: [{"subject": str, "predicate": str, "object": str}]
    """
    if not entities:
        return []

    entities_str = "\n".join([f"- {e.get('name')} ({e.get('type')})" for e in entities])

    prompt = f"""You are a Relationship Extraction Agent.

Analyze the text and the list of entities below. Identify relationships between these entities.
Represent every relationship as a semantic triple: Subject -> Predicate -> Object.

The Predicate should be a short lowercase active verb or relation (e.g. studied_at, uses, written_by, located_in, used_in, related_to, worked_at, developed, has_degree).
Both Subject and Object MUST refer to the names in the provided Entities list.

Return the relationships as a JSON list of objects, where each object has:
- "subject": the name of the subject entity
- "predicate": the relationship predicate
- "object": the name of the object entity

Example output:
[
  {{"subject": "V Nanda Jaya Krishna", "predicate": "studied_at", "object": "MRCET University"}},
  {{"subject": "Brain Tumor Detection Using CNN", "predicate": "uses", "object": "CNN"}}
]

Do not return any conversational text. Return only the raw JSON array.

Text:
{text}

Entities:
{entities_str}
"""
    try:
        response = model.generate_content(prompt)
        resp_text = response.text.strip()
        
        # Clean JSON markdown blocks if present
        if "```" in resp_text:
            resp_text = resp_text.split("```")[1]
            if resp_text.startswith("json"):
                resp_text = resp_text[4:].strip()
                
        # Find bounds of JSON array
        start = resp_text.find('[')
        end = resp_text.rfind(']')
        if start != -1 and end != -1 and end > start:
            resp_text = resp_text[start:end+1]
            
        return json.loads(resp_text)
    except Exception:
        # Fallback to empty list on parsing failure
        return []
