from collections import deque

class MemoryAgent:
    """
    Agent responsible for maintaining in-memory short-term conversational history.
    Limits memory to the most recent 10 exchanges per workspace segment.
    """
    def __init__(self, max_exchanges=10):
        # Maps workspace_id -> deque of (question, answer)
        self.workspace_histories = {}
        self.max_exchanges = max_exchanges

    def add_exchange(self, question, answer, workspace_id="default"):
        if workspace_id not in self.workspace_histories:
            self.workspace_histories[workspace_id] = deque(maxlen=self.max_exchanges)
        self.workspace_histories[workspace_id].append((question, answer))

    def get_history(self, workspace_id="default"):
        if workspace_id not in self.workspace_histories:
            self.workspace_histories[workspace_id] = deque(maxlen=self.max_exchanges)
        return list(self.workspace_histories[workspace_id])

    def clear(self, workspace_id="default"):
        if workspace_id in self.workspace_histories:
            self.workspace_histories[workspace_id].clear()


# Shared singleton instance for the process lifetime
_memory_instance = MemoryAgent()


def add_to_memory(question, answer, workspace_id="default"):
    """
    Record a conversation turn.
    """
    _memory_instance.add_exchange(question, answer, workspace_id=workspace_id)


def get_conversation_history(workspace_id="default"):
    """
    Retrieve the current conversation history.
    """
    return _memory_instance.get_history(workspace_id=workspace_id)


def clear_memory(workspace_id="default"):
    """
    Reset conversational memory.
    """
    _memory_instance.clear(workspace_id=workspace_id)
