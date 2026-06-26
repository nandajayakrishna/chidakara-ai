import uuid
import threading
from datetime import datetime
from typing import List, Dict, Any, Tuple

class ThreadSafeDict(dict):
    """
    Thread-safe subclass of standard dict, synchronizing access to keys/values.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()

    def __getitem__(self, key):
        with self._lock:
            return super().__getitem__(key)

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)

    def get(self, key, default=None):
        with self._lock:
            return super().get(key, default)

    def update(self, *args, **kwargs):
        with self._lock:
            super().update(*args, **kwargs)

    def keys(self):
        with self._lock:
            return list(super().keys())

    def values(self):
        with self._lock:
            return list(super().values())

    def items(self):
        with self._lock:
            return list(super().items())

    def __contains__(self, item):
        with self._lock:
            return super().__contains__(item)

    def __repr__(self):
        with self._lock:
            return super().__repr__()


class ThreadSafeList(list):
    """
    Thread-safe subclass of standard list, synchronizing mutations and iteration.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()

    def append(self, item):
        with self._lock:
            super().append(item)

    def extend(self, iterable):
        with self._lock:
            super().extend(iterable)

    def insert(self, index, item):
        with self._lock:
            super().insert(index, item)

    def remove(self, item):
        with self._lock:
            super().remove(item)

    def pop(self, index=-1):
        with self._lock:
            return super().pop(index)

    def clear(self):
        with self._lock:
            super().clear()

    def __getitem__(self, index):
        with self._lock:
            return super().__getitem__(index)

    def __setitem__(self, index, value):
        with self._lock:
            super().__setitem__(index, value)

    def __len__(self):
        with self._lock:
            return super().__len__()

    def __iter__(self):
        with self._lock:
            return iter(list(super().copy()))

    def __repr__(self):
        with self._lock:
            return super().__repr__()


class ExecutionContext:
    """
    Shared execution context containing all data accumulated and required
    by agents throughout the execution of a workflow. Guaranteed thread-safe.
    """
    def __init__(self, question: str, conversation_history: List[Tuple[str, str]] = None):
        self._lock = threading.Lock()
        self.trace_id: str = str(uuid.uuid4())
        self.workspace_id: str = "default"
        self._question: str = question
        self._retrieved_documents = ThreadSafeList()
        self._metadata = ThreadSafeList()
        self._conversation_history = ThreadSafeList(conversation_history or [])
        self._draft_answer: str = ""
        self._final_answer: str = ""
        self.tool_outputs = ThreadSafeDict()

# workflow execution state
        self.workflow_state = ThreadSafeDict()

# workspace state
        self.workspace_state = ThreadSafeDict()
        self._execution_trace = ThreadSafeList()
        self._web_results = ThreadSafeList()
        self._web_sources = ThreadSafeList()
        self._web_summary: str = ""
        self._web_status: str = "success"
        self._graph_nodes = ThreadSafeList()
        self._graph_edges = ThreadSafeList()
        self._graph_results: str = ""
        self._graph_status: str = "success"
        self.debug_metadata = ThreadSafeDict()
        self.reflection = ThreadSafeDict()
        self._confidence_score: float = 0.0
        self._confidence_reason: str = ""
        self.execution_plan = ThreadSafeDict()
        self._current_task: str = ""
        self._completed_tasks = ThreadSafeList()
        self._remaining_tasks = ThreadSafeList()
        self._plan_status: str = "pending"

    def record_trace(self, step: str, agent_name: str, status: str = "completed"):
        """
        Records the execution of a workflow step in the chronological trace.
        """
        self._execution_trace.append({
            "step": step,
            "agent": agent_name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })

    @property
    def question(self) -> str:
        with self._lock:
            return self._question

    @question.setter
    def question(self, value: str):
        with self._lock:
            self._question = value

    @property
    def retrieved_documents(self) -> List[str]:
        return self._retrieved_documents

    @retrieved_documents.setter
    def retrieved_documents(self, value: List[str]):
        self._retrieved_documents = ThreadSafeList(value)

    @property
    def metadata(self) -> List[Dict[str, Any]]:
        return self._metadata

    @metadata.setter
    def metadata(self, value: List[Dict[str, Any]]):
        self._metadata = ThreadSafeList(value)

    @property
    def conversation_history(self) -> List[Tuple[str, str]]:
        return self._conversation_history

    @conversation_history.setter
    def conversation_history(self, value: List[Tuple[str, str]]):
        self._conversation_history = ThreadSafeList(value)

    @property
    def draft_answer(self) -> str:
        with self._lock:
            return self._draft_answer

    @draft_answer.setter
    def draft_answer(self, value: str):
        with self._lock:
            self._draft_answer = value

    @property
    def final_answer(self) -> str:
        with self._lock:
            return self._final_answer

    @final_answer.setter
    def final_answer(self, value: str):
        with self._lock:
            self._final_answer = value

    @property
    def execution_trace(self) -> List[Dict[str, Any]]:
        return self._execution_trace

    @execution_trace.setter
    def execution_trace(self, value: List[Dict[str, Any]]):
        self._execution_trace = ThreadSafeList(value)

    @property
    def trace(self) -> List[Dict[str, Any]]:
        return self._execution_trace

    @trace.setter
    def trace(self, value: List[Dict[str, Any]]):
        self._execution_trace = ThreadSafeList(value)

    @property
    def web_results(self) -> List[Dict[str, Any]]:
        return self._web_results

    @web_results.setter
    def web_results(self, value: List[Dict[str, Any]]):
        self._web_results = ThreadSafeList(value)

    @property
    def web_sources(self) -> List[Dict[str, Any]]:
        return self._web_sources

    @web_sources.setter
    def web_sources(self, value: List[Dict[str, Any]]):
        self._web_sources = ThreadSafeList(value)

    @property
    def web_summary(self) -> str:
        with self._lock:
            return self._web_summary

    @web_summary.setter
    def web_summary(self, value: str):
        with self._lock:
            self._web_summary = value

    @property
    def web_status(self) -> str:
        with self._lock:
            return self._web_status

    @web_status.setter
    def web_status(self, value: str):
        with self._lock:
            self._web_status = value

    @property
    def graph_nodes(self) -> List[Dict[str, Any]]:
        return self._graph_nodes

    @graph_nodes.setter
    def graph_nodes(self, value: List[Dict[str, Any]]):
        self._graph_nodes = ThreadSafeList(value)

    @property
    def graph_edges(self) -> List[Dict[str, Any]]:
        return self._graph_edges

    @graph_edges.setter
    def graph_edges(self, value: List[Dict[str, Any]]):
        self._graph_edges = ThreadSafeList(value)

    @property
    def graph_results(self) -> str:
        with self._lock:
            return self._graph_results

    @graph_results.setter
    def graph_results(self, value: str):
        with self._lock:
            self._graph_results = value

    @property
    def graph_status(self) -> str:
        with self._lock:
            return self._graph_status

    @graph_status.setter
    def graph_status(self, value: str):
        with self._lock:
            self._graph_status = value

    @property
    def confidence_score(self) -> float:
        with self._lock:
            return self._confidence_score

    @confidence_score.setter
    def confidence_score(self, value: float):
        with self._lock:
            self._confidence_score = value

    @property
    def confidence_reason(self) -> str:
        with self._lock:
            return self._confidence_reason

    @confidence_reason.setter
    def confidence_reason(self, value: str):
        with self._lock:
            self._confidence_reason = value

    @property
    def current_task(self) -> str:
        with self._lock:
            return self._current_task

    @current_task.setter
    def current_task(self, value: str):
        with self._lock:
            self._current_task = value

    @property
    def completed_tasks(self) -> List[str]:
        return self._completed_tasks

    @completed_tasks.setter
    def completed_tasks(self, value: List[str]):
        self._completed_tasks = ThreadSafeList(value)

    @property
    def remaining_tasks(self) -> List[str]:
        return self._remaining_tasks

    @remaining_tasks.setter
    def remaining_tasks(self, value: List[str]):
        self._remaining_tasks = ThreadSafeList(value)

    @property
    def plan_status(self) -> str:
        with self._lock:
            return self._plan_status

    @plan_status.setter
    def plan_status(self, value: str):
        with self._lock:
            self._plan_status = value
