from typing import List, Dict, Any

class Task:
    """
    Represents a single subtask within an ExecutionPlan.
    """
    def __init__(self, task_id: str, task_name: str, description: str, agent_workflow: List[str], dependencies: List[str] = None, priority: int = 1):
        self.task_id = task_id
        self.task_name = task_name
        self.description = description
        self.agent_workflow = agent_workflow  # List of agent steps (e.g. ["research", "knowledge", "reflection", "critic"])
        self.dependencies = dependencies or []
        self.priority = priority
        self.status = "pending"  # pending, running, completed, failed
        self.result = ""
        self.duration = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "description": self.description,
            "agent_workflow": self.agent_workflow,
            "dependencies": self.dependencies,
            "priority": self.priority,
            "status": self.status,
            "result": self.result,
            "duration": round(self.duration, 2)
        }

class ExecutionPlan:
    """
    Represents a full multi-task plan decomposed from a user's complex goal.
    """
    def __init__(self, goal: str, tasks: List[Task] = None):
        self.goal = goal
        self.tasks: List[Task] = tasks or []
        self.status = "pending"  # pending, running, completed, failed
        self.current_task_id = ""

    def add_task(self, task: Task):
        self.tasks.append(task)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "tasks": [t.to_dict() for t in self.tasks],
            "status": self.status,
            "current_task_id": self.current_task_id,
            "completed_steps": [t.task_id for t in self.tasks if t.status == "completed"]
        }
