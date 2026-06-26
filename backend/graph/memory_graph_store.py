from typing import List, Dict, Any, Optional
from graph.base_graph_store import GraphStore
from graph.graph_models import Node, Relationship

class MemoryGraphStore(GraphStore):
    """
    In-memory implementation of the GraphStore interface.
    """
    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self._edges: List[Relationship] = []

    def _normalize_id(self, node_id: str) -> str:
        return node_id.strip()

    def add_node(self, node_id: str, label: str, properties: Optional[Dict[str, Any]] = None) -> None:
        nid = self._normalize_id(node_id)
        # If node exists, merge properties
        if nid in self._nodes:
            self._nodes[nid].properties.update(properties or {})
            if label and label != "Entity":
                self._nodes[nid].label = label
        else:
            self._nodes[nid] = Node(nid, label, properties)

    def add_edge(self, source_id: str, target_id: str, predicate: str, properties: Optional[Dict[str, Any]] = None) -> None:
        src = self._normalize_id(source_id)
        tgt = self._normalize_id(target_id)
        
        # Ensure source and target nodes exist in the graph
        if src not in self._nodes:
            self.add_node(src, "Entity")
        if tgt not in self._nodes:
            self.add_node(tgt, "Entity")
            
        # Avoid duplicate edges with exact same source, target, and predicate
        for edge in self._edges:
            if edge.source == src and edge.target == tgt and edge.predicate == predicate:
                edge.properties.update(properties or {})
                return
                
        self._edges.append(Relationship(src, tgt, predicate, properties))

    def find_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        nid = self._normalize_id(node_id)
        # Case-insensitive lookup helper
        for key, node in self._nodes.items():
            if key.lower() == nid.lower():
                return node.to_dict()
        return None

    def neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        nid = self._normalize_id(node_id).lower()
        connected = []
        
        for edge in self._edges:
            if edge.source.lower() == nid:
                target_node = self._nodes.get(edge.target)
                if target_node:
                    connected.append({
                        "node": target_node.to_dict(),
                        "relationship": edge.predicate,
                        "direction": "outgoing",
                        "properties": edge.properties
                    })
            elif edge.target.lower() == nid:
                source_node = self._nodes.get(edge.source)
                if source_node:
                    connected.append({
                        "node": source_node.to_dict(),
                        "relationship": edge.predicate,
                        "direction": "incoming",
                        "properties": edge.properties
                    })
        return connected

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for nodes matching a substring search of ID or Label.
        """
        q = query.lower().strip()
        matched = []
        for node in self._nodes.values():
            if q in node.id.lower() or q in node.label.lower():
                matched.append(node.to_dict())
        return matched

    def serialize(self) -> Dict[str, Any]:
        """
        Returns full graph as a dictionary of nodes and edges.
        """
        return {
            "nodes": [node.to_dict() for node in self._nodes.values()],
            "edges": [edge.to_dict() for edge in self._edges]
        }
