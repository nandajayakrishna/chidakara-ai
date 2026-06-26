from typing import List, Dict, Any, Optional

class GraphStore:
    """
    Abstract Base Class defining the standard interface for all Knowledge Graph Stores.
    """
    def add_node(self, node_id: str, label: str, properties: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

    def add_edge(self, source_id: str, target_id: str, predicate: str, properties: Optional[Dict[str, Any]] = None) -> None:
        raise NotImplementedError

    def find_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def neighbors(self, node_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def search(self, query: str) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def serialize(self) -> Dict[str, Any]:
        raise NotImplementedError
