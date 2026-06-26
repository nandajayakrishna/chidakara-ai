from typing import List
from graph.base_graph_store import GraphStore
from graph.entity_extractor import extract_entities
from graph.relationship_extractor import extract_relationships

def build_graph_from_documents(store: GraphStore, documents: List[str]) -> None:
    """
    Parses a list of documents, extracts entities and relationships,
    and loads them into the provided GraphStore.
    """
    for doc in documents:
        # 1. Extract and ingest nodes
        entities = extract_entities(doc)
        for entity in entities:
            name = entity.get("name")
            label = entity.get("type", "Entity")
            if name:
                store.add_node(name, label)
                
        # 2. Extract and ingest edges (relationships)
        relationships = extract_relationships(doc, entities)
        for rel in relationships:
            subj = rel.get("subject")
            obj = rel.get("object")
            pred = rel.get("predicate")
            if subj and obj and pred:
                store.add_edge(subj, obj, pred)
