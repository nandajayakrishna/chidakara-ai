import concurrent.futures
import time
from typing import List
from workflow.workflow_graph import WorkflowNode

def run_parallel_stage(stage_nodes: List[WorkflowNode], ctx) -> None:
    """
    Executes a list of independent workflow nodes concurrently.
    All exceptions raised during concurrent thread execution are propagated cleanly.
    """
    if not stage_nodes:
        return
        
    # Execute node functions concurrently in a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(stage_nodes)) as executor:
        futures = {}
        for node in stage_nodes:
            node.status = "running"
            node.start_time = time.time()
            
            # Submit callable task with shared ExecutionContext
            futures[executor.submit(node.callable, ctx)] = node
            
        # Wait for all futures to resolve
        for future in concurrent.futures.as_completed(futures):
            node = futures[future]
            try:
                future.result()
                node.status = "completed"
            except Exception as e:
                node.status = "failed"
                raise e
            finally:
                node.end_time = time.time()
                node.duration = (node.end_time - node.start_time) * 1000.0
