from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseConnector(ABC):
    """
    Abstract Base Class defining the required interface for all Enterprise Connectors.
    Each external provider (GitHub, Google Drive, etc.) must subclass this.
    """
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.is_connected = False
        self.config: Dict[str, Any] = {}

    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> bool:
        """
        Establish connection to the external provider using credentials.
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Sever connection and clear configurations.
        """
        pass

    @abstractmethod
    def sync(self, mode: str = "full", last_sync_time: float = 0.0) -> List[Dict[str, Any]]:
        """
        Fetch data from the provider. Supports 'full' or 'incremental' mode.
        Returns a list of standardized normalized dictionaries.
        """
        pass

    @abstractmethod
    def status(self) -> Dict[str, Any]:
        """
        Retrieve provider health and connection parameters.
        """
        pass

    @abstractmethod
    def metadata(self) -> Dict[str, Any]:
        """
        Provide information about the connector capabilities.
        """
        pass

    @abstractmethod
    def supported_objects(self) -> List[str]:
        """
        Return a list of normalized object types supported by this connector.
        e.g., ["Repository", "User", "Task"] for GitHub.
        """
        pass
