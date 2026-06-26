import time
from typing import Dict, Any, List, Optional
from connectors.providers.mock_providers import (
    GitHubConnector, GoogleDriveConnector, SlackConnector, JiraConnector,
    NotionConnector, GmailConnector, ConfluenceConnector, SharePointConnector
)
from organization.models.org_graph import org_graph_instance

class SyncEngine:
    """
    Orchestrates synchronization runs, health reports, and logs histories.
    Integrates external data structures directly into Chidakara's corporate knowledge graph.
    """
    def __init__(self):
        # Instantiate connectors
        self.connectors: Dict[str, Any] = {
            "GitHub": GitHubConnector(),
            "GoogleDrive": GoogleDriveConnector(),
            "Slack": SlackConnector(),
            "Jira": JiraConnector(),
            "Notion": NotionConnector(),
            "Gmail": GmailConnector(),
            "Confluence": ConfluenceConnector(),
            "SharePoint": SharePointConnector()
        }
        
        # Track last sync timestamps
        self.last_sync_times: Dict[str, float] = {}
        
        # In-memory sync history log
        self.sync_history: List[Dict[str, Any]] = []

    def get_connectors_info(self) -> List[Dict[str, Any]]:
        """
        List all connectors and their active configurations and status.
        """
        info = []
        for name, conn in self.connectors.items():
            status = conn.status()
            metadata = conn.metadata()
            info.append({
                "provider": name,
                "name": metadata.get("name"),
                "version": metadata.get("version"),
                "api_endpoint": metadata.get("api_endpoint"),
                "connected": conn.is_connected,
                "supported_objects": conn.supported_objects(),
                "status": status,
                "last_sync": self.last_sync_times.get(name, 0.0)
            })
        return info

    def connect_provider(self, provider: str, config: Dict[str, Any]) -> bool:
        conn = self.connectors.get(provider)
        if conn:
            return conn.connect(config)
        return False

    def disconnect_provider(self, provider: str) -> bool:
        conn = self.connectors.get(provider)
        if conn:
            return conn.disconnect()
        return False

    def get_status(self) -> Dict[str, Any]:
        """
        Returns general connection metrics.
        """
        connected_count = sum(1 for c in self.connectors.values() if c.is_connected)
        total_connectors = len(self.connectors)
        
        # Calculate a simple aggregate health score
        active_statuses = [c.status() for c in self.connectors.values() if c.is_connected]
        avg_health = sum(s.get("health_score", 100) for s in active_statuses) / len(active_statuses) if active_statuses else 100.0

        return {
            "connected_count": connected_count,
            "total_count": total_connectors,
            "health_score": round(avg_health, 1),
            "health_rating": "Excellent" if avg_health >= 95 else "Good" if avg_health >= 85 else "Needs Attention"
        }

    def sync_provider(self, provider: str, mode: str = "full") -> Dict[str, Any]:
        conn = self.connectors.get(provider)
        if not conn:
            return {"success": False, "error": f"Provider '{provider}' not registered."}
        
        if not conn.is_connected:
            return {"success": False, "error": f"Provider '{provider}' is not connected. Configure credentials first."}

        start_time = time.time()
        last_sync = self.last_sync_times.get(provider, 0.0)
        
        try:
            # 1. Retrieve standardized entities from mock API
            entities = conn.sync(mode, last_sync)
            
            # 2. Ingest into Chidakara's active Knowledge Graph
            self._ingest_into_knowledge_graph(entities, provider)
            
            duration_ms = int((time.time() - start_time) * 1000)
            self.last_sync_times[provider] = start_time

            # Log history entry
            history_entry = {
                "id": f"job-{int(start_time)}-{provider}",
                "provider": provider,
                "mode": mode,
                "timestamp": start_time,
                "duration_ms": duration_ms,
                "items_count": len(entities),
                "status": "Success",
                "errors": []
            }
            self.sync_history.append(history_entry)
            
            return {
                "success": True,
                "job_id": history_entry["id"],
                "items_synced": len(entities),
                "duration_ms": duration_ms
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            history_entry = {
                "id": f"job-{int(start_time)}-{provider}",
                "provider": provider,
                "mode": mode,
                "timestamp": start_time,
                "duration_ms": duration_ms,
                "items_count": 0,
                "status": "Failure",
                "errors": [str(e)]
            }
            self.sync_history.append(history_entry)
            return {"success": False, "error": str(e)}

    def _ingest_into_knowledge_graph(self, entities: List[Dict[str, Any]], provider: str):
        """
        Converts standardized entity fields and injects them directly into org_graph_instance.
        """
        for item in entities:
            entity_id = item["id"]
            entity_type = item["type"]
            props = item["properties"]
            name = props.get("name") or props.get("title") or entity_id

            # Simple Conflict Detection (Last Write Wins)
            existing_node = org_graph_instance.find_node(entity_id)
            if existing_node:
                # Check timestamp if exists in properties
                existing_time = existing_node.get("properties", {}).get("sync_timestamp", 0.0)
                if item["timestamp"] <= existing_time:
                    # Target node is newer, skip update to prevent regression
                    continue

            # Update timestamp metadata on properties
            props["sync_timestamp"] = item["timestamp"]
            props["data_source"] = provider

            # Map unified category class to graph labels
            graph_label = entity_type
            if entity_type in ["Page", "Email", "File"]:
                graph_label = "Document"
            elif entity_type in ["Issue"]:
                graph_label = "Task"

            # Ingest node
            org_graph_instance.add_node(entity_id, graph_label, props)

            # Establish standard relationships based on provider types
            if provider == "GitHub":
                if entity_type == "Repository":
                    org_graph_instance.add_edge("Repo_Chidakara_AI", entity_id, "DEPENDS_ON")
                elif entity_type == "User":
                    org_graph_instance.add_edge(entity_id, "Project_Chidakara", "WORKS_ON")
                    org_graph_instance.add_edge(entity_id, "AI_Core_Team", "PART_OF")
                elif entity_type == "Task":
                    # Assign task to creator or default to Gary
                    assignee = props.get("assignee", "Gary")
                    org_graph_instance.add_edge(entity_id, assignee, "ASSIGNED_TO")
                    org_graph_instance.add_edge(entity_id, "Project_Chidakara", "PART_OF")

            elif provider == "Slack":
                if entity_type == "User":
                    org_graph_instance.add_edge(entity_id, "Frontend_Team", "PART_OF")
                elif entity_type == "Message":
                    sender = props.get("sender")
                    if sender:
                        org_graph_instance.add_edge(sender, entity_id, "GENERATES")
                        org_graph_instance.add_edge(entity_id, "Project_Chidakara", "DISCUSSES")

            elif provider == "GoogleDrive" or provider == "Notion" or provider == "Confluence":
                # Ingest document references
                org_graph_instance.add_edge("Project_Chidakara", entity_id, "GENERATES")

            elif provider == "Jira":
                if entity_type == "Issue" or entity_type == "Task":
                    org_graph_instance.add_edge(entity_id, "Project_Chidakara", "PART_OF")
                    org_graph_instance.add_edge(entity_id, "Alice", "ASSIGNED_TO")

# Single global sync engine instance
sync_engine_instance = SyncEngine()
