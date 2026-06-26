import json
import re
from typing import List, Dict, Any
from rag.llm_client import model

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extracts key entities from text using the Gemini LLM.
    Returns a list of dicts: [{"name": str, "type": str}]
    """
    prompt = f"""You are an Entity Extraction Agent.

Analyze the text below and extract all key entities.
An entity can be a Person, University, Degree, Skill, Project, Publication, Company, Technology, Programming Language, Certification, Award, Event, Organization, Location, Date, or other relevant concepts.

Return the entities as a JSON list of objects, where each object has:
- "name": the canonical name of the entity
- "type": the entity type

Example output:
[
  {{"name": "Python", "type": "Programming Language"}},
  {{"name": "MRCET University", "type": "University"}}
]

Do not return any conversational text. Return only the raw JSON array.

Text:
{text}
"""
    try:
        response = model.generate_content(prompt)
        resp_text = response.text.strip()
        
        # Clean JSON markdown blocks if present
        if "```" in resp_text:
            resp_text = resp_text.split("```")[1]
            if resp_text.startswith("json"):
                resp_text = resp_text[4:].strip()
                
        # Find bounds of JSON array to be absolutely safe
        start = resp_text.find('[')
        end = resp_text.rfind(']')
        if start != -1 and end != -1 and end > start:
            resp_text = resp_text[start:end+1]
            
        return json.loads(resp_text)
    except Exception:
        # Fallback to empty list on parsing failure
        return []
