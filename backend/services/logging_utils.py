"""
Logging utilities for secure logging practices
"""
from typing import Any

def sanitize_for_logging(data: Any, max_length: int = 50) -> str:
    """
    Sanitize sensitive data for logging purposes.
    Returns a safe string representation without exposing sensitive content.
    
    Args:
        data: The data to sanitize
        max_length: Maximum length before truncation (default: 50)
        
    Returns:
        Safe string representation for logging
    """
    if data is None:
        return "None"
    
    data_type = type(data).__name__
    
    if isinstance(data, str):
        if len(data) > max_length:
            return f"<{data_type}: {len(data)} chars (truncated for security)>"
        return f"<{data_type}: {len(data)} chars>"
    elif isinstance(data, (dict, list)):
        return f"<{data_type}: {len(data)} items>"
    elif isinstance(data, bytes):
        return f"<bytes: {len(data)} bytes>"
    else:
        return f"<{data_type}>"
