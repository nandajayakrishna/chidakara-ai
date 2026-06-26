from typing import Dict, Any

class Node:
    """
    Represents an entity node in the Knowledge Graph.
    """
    def __init__(self, id: str, label: str, properties: Dict[str, Any] = None):
        self.id = id
        self.label = label  # e.g., Person, Skill, University
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "properties": self.properties
        }


class Relationship:
    """
    Represents a directed edge between two entity nodes.
    """
    def __init__(self, source: str, target: str, predicate: str, properties: Dict[str, Any] = None):
        self.source = source  # Node ID of source
        self.target = target  # Node ID of target
        self.predicate = predicate  # e.g., studied_at, uses
        self.properties = properties or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "predicate": self.predicate,
            "properties": self.properties
        }
