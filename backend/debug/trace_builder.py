import threading
from typing import List, Dict, Any, Optional

# Thread-safety mutex lock
_traces_lock = threading.Lock()
# In-memory storage list
_trace_history: List[Dict[str, Any]] = []

def save_trace(serialized_trace: Dict[str, Any]):
    """
    Saves a serialized execution trace to the in-memory store.
    """
    with _traces_lock:
        _trace_history.append(serialized_trace)

def get_latest_trace() -> Optional[Dict[str, Any]]:
    """
    Returns the most recent execution trace.
    """
    with _traces_lock:
        if _trace_history:
            return _trace_history[-1]
        return None

def get_trace_history() -> List[Dict[str, Any]]:
    """
    Returns all stored execution traces.
    """
    with _traces_lock:
        return list(_trace_history)

def get_trace_by_id(trace_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a single trace by its unique trace_id.
    """
    with _traces_lock:
        for trace in _trace_history:
            if trace.get("trace_id") == trace_id:
                return trace
        return None

def clear_traces():
    """
    Clears all execution traces in the store (primarily for unit testing).
    """
    with _traces_lock:
        _trace_history.clear()
