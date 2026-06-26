import time
from typing import Dict, Any, List, Callable

class WorkflowNode:
    """
    Represents a single task (agent execution step) in the dependency graph.
    """
    def __init__(self, id: str, callable_func: Callable, dependencies: List[str] = None):
        self.id = id
        self.callable = callable_func
        self.dependencies = dependencies or []
        self.status = "pending"  # pending, running, completed, failed
        self.start_time = 0.0
        self.end_time = 0.0
        self.duration = 0.0
        self.parallel_group = 1
        self.stage_number = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dependencies": self.dependencies,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "parallel_group": self.parallel_group,
            "stage_number": self.stage_number
        }

class WorkflowDAG:
    """
    Represents a Directed Acyclic Graph consisting of execution steps.
    """
    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}

    def add_node(self, id: str, callable_func: Callable, dependencies: List[str] = None) -> None:
        self.nodes[id] = WorkflowNode(id, callable_func, dependencies)

    def get_node(self, id: str) -> WorkflowNode:
        return self.nodes.get(id)

    def get_all_nodes(self) -> List[WorkflowNode]:
        return list(self.nodes.values())
