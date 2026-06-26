from typing import List, Dict, Any
from graph.base_graph_store import GraphStore

def search_entity(store: GraphStore, name: str) -> List[Dict[str, Any]]:
    """
    Search for nodes matching a substring search of the name.
    """
    return store.search(name)

def find_relationships(store: GraphStore, entity: str) -> List[Dict[str, Any]]:
    """
    Lists all connected relations (edges) for a given entity name.
    """
    return store.neighbors(entity)

def find_projects(store: GraphStore) -> List[Dict[str, Any]]:
    """
    Finds all nodes labeled as 'Project' in the graph.
    """
    data = store.serialize()
    return [node for node in data["nodes"] if node.get("label", "").lower() == "project"]

def find_skills(store: GraphStore) -> List[Dict[str, Any]]:
    """
    Finds all nodes labeled as 'Skill' or 'Programming Language' in the graph.
    """
    data = store.serialize()
    skills_labels = {"skill", "programming language", "technology"}
    return [node for node in data["nodes"] if node.get("label", "").lower() in skills_labels]

def find_publications(store: GraphStore) -> List[Dict[str, Any]]:
    """
    Finds all nodes labeled as 'Publication' in the graph.
    """
    data = store.serialize()
    return [node for node in data["nodes"] if node.get("label", "").lower() == "publication"]

def related_entities(store: GraphStore) -> List[Dict[str, Any]]:
    """
    Returns all relationship edges linking entities.
    """
    return store.serialize()["edges"]

def search_graph_with_llm(store: GraphStore, query: str) -> str:
    """
    Serializes the graph structure and requests Gemini LLM to semantically
    resolve the query against the graph's relationships.
    """
    data = store.serialize()
    if not data["nodes"]:
        return "No Knowledge Graph data found."
        
    nodes_str = "\n".join([f"- {node['id']} ({node['label']})" for node in data["nodes"]])
    edges_str = "\n".join([f"- {edge['source']} --[{edge['predicate']}]--> {edge['target']}" for edge in data["edges"]])
    
    prompt = f"""You are a Graph Search Agent.

Analyze the Knowledge Graph below and answer the query based strictly on the nodes and edges.
Provide a concise, accurate summary of matching connections and paths. Do not invent any facts.

Query:
{query}

Knowledge Graph:
Nodes:
{nodes_str}

Edges:
{edges_str}

Structured Search Results:
"""
    from rag.llm_client import model
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error traversing graph: {str(e)}"
