import sys
from datetime import datetime

def log_debug(message: str):
    """
    Logs a visual debugger debug message to stderr.
    """
    timestamp = datetime.now().isoformat()
    sys.stderr.write(f"[{timestamp}] [CHIDAKARA-DEBUG] {message}\n")

def log_error(message: str):
    """
    Logs a visual debugger error message to stderr.
    """
    timestamp = datetime.now().isoformat()
    sys.stderr.write(f"[{timestamp}] [CHIDAKARA-ERROR] {message}\n")
