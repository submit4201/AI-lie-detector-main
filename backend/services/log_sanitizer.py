"""
Utility for sanitizing sensitive information from log messages.
This prevents clear-text logging of user data, API responses, and other sensitive information.
"""
import json
import re
from typing import Any, Dict, Union


def sanitize_for_logging(data: Any, max_length: int = 100) -> str:
    """
    Sanitize data for logging by truncating and redacting sensitive information.
    
    Args:
        data: The data to sanitize (can be string, dict, list, etc.)
        max_length: Maximum length of the sanitized string
        
    Returns:
        A sanitized string safe for logging
    """
    if data is None:
        return "None"
    
    # Convert to string representation
    if isinstance(data, dict):
        # Redact potentially sensitive keys
        sanitized = _redact_sensitive_keys(data)
        data_str = json.dumps(sanitized, ensure_ascii=False)
    elif isinstance(data, str):
        data_str = data
    else:
        data_str = str(data)
    
    # Truncate to max_length
    if len(data_str) > max_length:
        return data_str[:max_length] + "... [truncated]"
    
    return data_str


def _redact_sensitive_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact values for keys that might contain sensitive information.
    
    Args:
        data: Dictionary to redact
        
    Returns:
        Dictionary with sensitive values redacted
    """
    # Keys that should be redacted
    sensitive_keys = {
        'transcript', 'transcripts', 'speaker_transcripts',
        'text', 'content', 'message', 'response',
        'api_key', 'token', 'password', 'secret',
        'raw_text', 'raw_response', 'gemini_raw_response',
        'error_details', 'stack_trace'
    }
    
    redacted = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if key contains sensitive information
        if any(sens_key in key_lower for sens_key in sensitive_keys):
            if isinstance(value, str):
                redacted[key] = f"[REDACTED: {len(value)} chars]"
            elif isinstance(value, (dict, list)):
                redacted[key] = f"[REDACTED: {type(value).__name__}]"
            else:
                redacted[key] = "[REDACTED]"
        elif isinstance(value, dict):
            redacted[key] = _redact_sensitive_keys(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            redacted[key] = [_redact_sensitive_keys(item) if isinstance(item, dict) else item for item in value[:3]]
            if len(value) > 3:
                redacted[key].append(f"... [{len(value) - 3} more items]")
        else:
            redacted[key] = value
    
    return redacted


def sanitize_error_message(error: Exception) -> str:
    """
    Sanitize an exception message for logging.
    Removes potentially sensitive information while keeping the error type.
    
    Args:
        error: The exception to sanitize
        
    Returns:
        A sanitized error message
    """
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Truncate long error messages
    if len(error_msg) > 200:
        error_msg = error_msg[:200] + "... [truncated]"
    
    # Redact potential file paths that might contain usernames
    error_msg = re.sub(r'/home/[^/]+/', '/home/[USER]/', error_msg)
    error_msg = re.sub(r'C:\\\\Users\\\\[^\\\\]+\\\\', r'C:\\Users\\[USER]\\', error_msg)
    
    return f"{error_type}: {error_msg}"


def sanitize_api_response(response_data: Dict[str, Any]) -> str:
    """
    Sanitize API response data for logging.
    
    Args:
        response_data: The API response to sanitize
        
    Returns:
        A sanitized string representation
    """
    if not response_data:
        return "Empty response"
    
    # Create a sanitized version showing only structure
    sanitized = {
        "response_type": type(response_data).__name__,
        "keys": list(response_data.keys()) if isinstance(response_data, dict) else "N/A",
        "has_error": "error" in response_data if isinstance(response_data, dict) else False
    }
    
    return json.dumps(sanitized)
