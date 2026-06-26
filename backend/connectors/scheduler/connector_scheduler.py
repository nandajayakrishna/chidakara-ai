import time
from typing import Dict, Any, List

class ConnectorScheduler:
    """
    Mock background scheduler for triggering automated connector syncs.
    In real implementations, this would map to a Cron, Celery, or APScheduler worker.
    """
    def __init__(self):
        self.jobs: List[Dict[str, Any]] = [
            {
                "id": "sched-job-github",
                "provider": "GitHub",
                "interval_minutes": 60,
                "mode": "incremental",
                "enabled": True,
                "next_run": time.time() + 3600
            },
            {
                "id": "sched-job-gdrive",
                "provider": "GoogleDrive",
                "interval_minutes": 360,
                "mode": "full",
                "enabled": False,
                "next_run": time.time() + 21600
            }
        ]

    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        return self.jobs

    def toggle_job(self, job_id: str, enabled: bool) -> bool:
        for job in self.jobs:
            if job["id"] == job_id:
                job["enabled"] = enabled
                return True
        return False
