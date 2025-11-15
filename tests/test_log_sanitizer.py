"""
Unit tests for log sanitization utility to prevent clear-text logging of sensitive information.
"""
import pytest
from backend.services.log_sanitizer import (
    sanitize_for_logging, 
    sanitize_error_message, 
    sanitize_api_response,
    _redact_sensitive_keys
)


def test_sanitize_string_truncation():
    """Test that long strings are properly truncated"""
    long_string = "a" * 200
    result = sanitize_for_logging(long_string, max_length=100)
    assert len(result) <= 115  # 100 + "... [truncated]"
    assert result.endswith("... [truncated]")


def test_sanitize_none():
    """Test handling of None values"""
    result = sanitize_for_logging(None)
    assert result == "None"


def test_redact_sensitive_keys():
    """Test that sensitive keys are properly redacted"""
    data = {
        "transcript": "This is sensitive user data",
        "api_key": "secret_key_123",
        "credibility_score": 75,
        "raw_response": {"nested": "data"}
    }
    
    result = _redact_sensitive_keys(data)
    
    # Sensitive data should be redacted
    assert "[REDACTED:" in result["transcript"]
    assert "secret_key_123" not in str(result)
    
    # Non-sensitive data should remain
    assert result["credibility_score"] == 75


def test_redact_nested_sensitive_data():
    """Test that nested sensitive data is redacted"""
    data = {
        "analysis": {
            "transcript": "User said something",
            "score": 90
        },
        "metadata": {
            "session_id": "abc123"
        }
    }
    
    result = _redact_sensitive_keys(data)
    
    # Nested transcript should be redacted
    assert "[REDACTED:" in result["analysis"]["transcript"]
    
    # Non-sensitive nested data should remain
    assert result["analysis"]["score"] == 90
    assert result["metadata"]["session_id"] == "abc123"


def test_sanitize_error_message():
    """Test that error messages are properly sanitized"""
    try:
        raise ValueError("This is a very long error message " + "x" * 300)
    except Exception as e:
        result = sanitize_error_message(e)
        
        # Should include error type
        assert "ValueError:" in result
        
        # Should be truncated
        assert len(result) < 250


def test_sanitize_error_message_with_path():
    """Test that file paths are redacted in error messages"""
    try:
        raise IOError("/home/johndoe/secret/file.txt not found")
    except Exception as e:
        result = sanitize_error_message(e)
        
        # Username should be redacted
        assert "johndoe" not in result
        assert "[USER]" in result


def test_sanitize_api_response():
    """Test that API responses show structure only"""
    response = {
        "transcript": "Sensitive user data here",
        "analysis": {
            "score": 85,
            "details": "More sensitive data"
        },
        "error": None
    }
    
    result = sanitize_api_response(response)
    
    # Should not contain actual sensitive data
    assert "Sensitive user data" not in result
    
    # Should show structure
    assert "response_type" in result
    assert "keys" in result


def test_sanitize_empty_response():
    """Test handling of empty responses"""
    result = sanitize_api_response(None)
    assert result == "Empty response"
    
    result = sanitize_api_response({})
    assert "response_type" in result


def test_sanitize_dict_with_list_values():
    """Test sanitization of dictionaries containing lists"""
    data = {
        "transcripts": [
            "First transcript",
            "Second transcript",
            "Third transcript",
            "Fourth transcript"
        ],
        "scores": [1, 2, 3, 4, 5]
    }
    
    result = _redact_sensitive_keys(data)
    
    # Transcripts should be redacted
    assert "[REDACTED:" in result["transcripts"]
    
    # Non-sensitive list should remain but may be truncated
    assert "scores" in result


def test_sanitize_for_logging_with_dict():
    """Test sanitizing a dictionary for logging"""
    data = {
        "text": "User's sensitive text",
        "score": 95,
        "password": "secret123"
    }
    
    result = sanitize_for_logging(data, max_length=200)
    
    # Sensitive keys should be redacted
    assert "User's sensitive text" not in result
    assert "secret123" not in result
    
    # Should be valid format
    assert isinstance(result, str)


def test_long_dict_truncation():
    """Test that large dictionaries are properly truncated"""
    data = {f"key_{i}": f"value_{i}" * 100 for i in range(50)}
    
    result = sanitize_for_logging(data, max_length=100)
    
    assert len(result) <= 115  # 100 + "... [truncated]"
    assert result.endswith("... [truncated]")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
