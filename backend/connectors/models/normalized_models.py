from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class NormalizedEntity:
    id: str
    type: str # User, Project, Repository, Message, Document, Issue, Task, Page, Email, File
    timestamp: float # Last modified timestamp
    properties: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "timestamp": self.timestamp,
            "properties": self.properties
        }

@dataclass
class NormalizedUser(NormalizedEntity):
    def __init__(self, id: str, name: str, email: str, role: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"name": name, "email": email, "role": role})
        super().__init__(id, "User", timestamp, props)

@dataclass
class NormalizedProject(NormalizedEntity):
    def __init__(self, id: str, name: str, status: str, priority: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"name": name, "status": status, "priority": priority})
        super().__init__(id, "Project", timestamp, props)

@dataclass
class NormalizedRepository(NormalizedEntity):
    def __init__(self, id: str, name: str, status: str, url: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"name": name, "status": status, "url": url})
        super().__init__(id, "Repository", timestamp, props)

@dataclass
class NormalizedMessage(NormalizedEntity):
    def __init__(self, id: str, sender: str, channel: str, text: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"sender": sender, "channel": channel, "text": text})
        super().__init__(id, "Message", timestamp, props)

@dataclass
class NormalizedDocument(NormalizedEntity):
    def __init__(self, id: str, name: str, status: str, version: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"name": name, "status": status, "version": version})
        super().__init__(id, "Document", timestamp, props)

@dataclass
class NormalizedIssue(NormalizedEntity):
    def __init__(self, id: str, title: str, status: str, severity: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"title": title, "status": status, "severity": severity})
        super().__init__(id, "Issue", timestamp, props)

@dataclass
class NormalizedTask(NormalizedEntity):
    def __init__(self, id: str, name: str, status: str, assignee: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"name": name, "status": status, "assignee": assignee})
        super().__init__(id, "Task", timestamp, props)

@dataclass
class NormalizedPage(NormalizedEntity):
    def __init__(self, id: str, title: str, author: str, space: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"title": title, "author": author, "space": space})
        super().__init__(id, "Page", timestamp, props)

@dataclass
class NormalizedEmail(NormalizedEntity):
    def __init__(self, id: str, subject: str, sender: str, recipient: str, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"subject": subject, "sender": sender, "recipient": recipient})
        super().__init__(id, "Email", timestamp, props)

@dataclass
class NormalizedFile(NormalizedEntity):
    def __init__(self, id: str, name: str, file_type: str, size_bytes: int, timestamp: float, properties: Optional[Dict[str, Any]] = None):
        props = properties or {}
        props.update({"name": name, "file_type": file_type, "size_bytes": size_bytes})
        super().__init__(id, "File", timestamp, props)
