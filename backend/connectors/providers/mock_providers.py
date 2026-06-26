import time
from typing import Dict, Any, List
from connectors.base.connector import BaseConnector
from connectors.models.normalized_models import (
    NormalizedUser, NormalizedProject, NormalizedRepository, NormalizedMessage,
    NormalizedDocument, NormalizedIssue, NormalizedTask, NormalizedPage,
    NormalizedEmail, NormalizedFile
)

class GitHubConnector(BaseConnector):
    def __init__(self):
        super().__init__("GitHub")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        # 1. Repositories
        repo1 = NormalizedRepository("Repo_Next_App", "next-app-repository", "Active", "https://github.com/org/next-app", now - 3600)
        repo2 = NormalizedRepository("Repo_Custom_Adapter", "custom-adapter-tool", "Archived", "https://github.com/org/custom-adapter", now - 86400 * 5)
        
        # 2. Users
        user1 = NormalizedUser("Gary", "Gary Miller", "gary@company.com", "Senior Backend Dev", now - 7200)
        user2 = NormalizedUser("Helen", "Helen Carter", "helen@company.com", "AI Researcher", now - 86400)

        # 3. Issues
        issue1 = NormalizedIssue("Issue_Fix_Auth", "Fix Next.js OAuth refresh crash", "Open", "High", now - 1800)

        # 4. Tasks
        task1 = NormalizedTask("Task_Update_Node", "Update Node runtime versions in workflow", "In_Progress", "Gary", now - 600)

        all_items = [repo1, repo2, user1, user2, issue1, task1]

        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 42 if self.is_connected else 0,
            "health_score": 98 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "GitHub Enterprise Connector",
            "version": "1.2.0",
            "api_endpoint": "https://api.github.com"
        }

    def supported_objects(self) -> List[str]:
        return ["Repository", "User", "Issue", "Task"]


class GoogleDriveConnector(BaseConnector):
    def __init__(self):
        super().__init__("GoogleDrive")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        doc1 = NormalizedDocument("Doc_Marketing_Plan_2026", "Marketing Strategy Plan 2026", "Up_To_Date", "2.0", now - 7200)
        file1 = NormalizedFile("File_Spreadsheet_Q2_Budget", "Q2 Financial Budget Sheet", "xlsx", 409600, now - 86400 * 2)

        all_items = [doc1, file1]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 55 if self.is_connected else 0,
            "health_score": 100 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Google Workspace Drive Connector",
            "version": "1.0.4",
            "api_endpoint": "https://www.googleapis.com/drive/v3"
        }

    def supported_objects(self) -> List[str]:
        return ["Document", "File"]


class SlackConnector(BaseConnector):
    def __init__(self):
        super().__init__("Slack")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        user1 = NormalizedUser("Ian", "Ian Malcolm", "ian@company.com", "Chaos Engineer", now - 17200)
        user2 = NormalizedUser("Jane", "Jane Doe", "jane@company.com", "Tech Lead", now - 86400 * 4)

        msg1 = NormalizedMessage("Msg_Slack_1", "Ian", "dev-channel", "Has anyone deployed the Chidakara API v3 yet?", now - 300)
        msg2 = NormalizedMessage("Msg_Slack_2", "Jane", "dev-channel", "Yes, app is up and running at port 8000.", now - 200)

        all_items = [user1, user2, msg1, msg2]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 28 if self.is_connected else 0,
            "health_score": 95 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Slack Enterprise Slackbot Connector",
            "version": "2.1.0",
            "api_endpoint": "https://slack.com/api"
        }

    def supported_objects(self) -> List[str]:
        return ["User", "Message"]


class JiraConnector(BaseConnector):
    def __init__(self):
        super().__init__("Jira")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        issue1 = NormalizedIssue("Jira_Issue_1", "Pipeline memory leak in runner thread", "In_Progress", "High", now - 3600)
        task1 = NormalizedTask("Jira_Task_Optimize", "Optimize parallel topology schedules", "Completed", "Alice", now - 86400)

        all_items = [issue1, task1]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 85 if self.is_connected else 0,
            "health_score": 90 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Atlassian Jira Project Cloud Connector",
            "version": "1.4.1",
            "api_endpoint": "https://api.atlassian.com/ex/jira"
        }

    def supported_objects(self) -> List[str]:
        return ["Issue", "Task"]


class NotionConnector(BaseConnector):
    def __init__(self):
        super().__init__("Notion")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        page1 = NormalizedPage("Page_Notion_Roadmap", "Notion Core Architecture Roadmap", "Diana", "Product Space", now - 3600 * 4)
        doc1 = NormalizedDocument("Doc_Notion_Brief", "Engineering Sprint Overview Notion Doc", "Up_To_Date", "1.0", now - 86400 * 3)

        all_items = [page1, doc1]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 48 if self.is_connected else 0,
            "health_score": 97 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Notion API Workspace Connector",
            "version": "1.1.2",
            "api_endpoint": "https://api.notion.com/v1"
        }

    def supported_objects(self) -> List[str]:
        return ["Page", "Document"]


class GmailConnector(BaseConnector):
    def __init__(self):
        super().__init__("Gmail")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        email1 = NormalizedEmail("Email_Client_Intro", "Introduction to Chidakara AI Core capabilities", "client@external.com", "diana@company.com", now - 1800)

        all_items = [email1]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 64 if self.is_connected else 0,
            "health_score": 99 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Google Workspace Gmail Connector",
            "version": "1.0.1",
            "api_endpoint": "https://gmail.googleapis.com"
        }

    def supported_objects(self) -> List[str]:
        return ["Email"]


class ConfluenceConnector(BaseConnector):
    def __init__(self):
        super().__init__("Confluence")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        page1 = NormalizedPage("Page_Confluence_Sprint3", "Sprint 3.0 Planning Retro Notes", "Diana", "Engineering Space", now - 3600 * 12)

        all_items = [page1]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 90 if self.is_connected else 0,
            "health_score": 92 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Confluence Wiki Space Connector",
            "version": "1.2.5",
            "api_endpoint": "https://api.atlassian.com/ex/confluence"
        }

    def supported_objects(self) -> List[str]:
        return ["Page"]


class SharePointConnector(BaseConnector):
    def __init__(self):
        super().__init__("SharePoint")

    def connect(self, config: Dict[str, Any]) -> bool:
        self.config = config
        self.is_connected = True
        return True

    def disconnect(self) -> bool:
        self.config = {}
        self.is_connected = False
        return True

    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        now = time.time()
        entities = []

        file1 = NormalizedFile("Sharepoint_File_Specs", "Compliance Requirements Specification Doc", "docx", 819200, now - 86400 * 3)

        all_items = [file1]
        for item in all_items:
            if mode == "full" or item.timestamp > last_sync_time:
                entities.append(item.to_dict())

        return entities

    def status(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected,
            "latency_ms": 110 if self.is_connected else 0,
            "health_score": 88 if self.is_connected else 0,
            "errors": []
        }

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": "Microsoft SharePoint Portal Connector",
            "version": "1.0.0",
            "api_endpoint": "https://graph.microsoft.com/v1.0/sites"
        }

    def supported_objects(self) -> List[str]:
        return ["File"]
