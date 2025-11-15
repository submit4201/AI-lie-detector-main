import json
import logging
import re
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

def extract_json_from_text(text: str) -> Optional[str]:
    """
    Extract JSON from text that might contain markdown code blocks or other formatting.
    Returns the cleaned JSON string or None if no JSON-like content is found.
    """
    if not text or not isinstance(text, str):
        return None
    
    text = text.strip()
    
    # Remove markdown code blocks
    if text.startswith('```json'):
        text = text[7:].strip()
        if text.endswith('```'):
            text = text[:-3].strip()
    elif text.startswith('```'):
        text = text[3:].strip()
        if text.endswith('```'):
            text = text[:-3].strip()
    
    # Look for JSON-like content between curly braces
    if not text.startswith('{') and not text.startswith('['):
        # Try to find JSON in the text
        json_match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if json_match:
            text = json_match.group(1)
        else:
            return None
    
    return text.strip()

def safe_json_parse(text: str, fallback_value: Any = None) -> Union[Dict[str, Any], Any]:
    """
    Safely parse JSON text with multiple fallback strategies.
    
    Args:
        text: The text to parse as JSON
        fallback_value: Value to return if parsing fails completely
    
    Returns:
        Parsed JSON object or fallback_value
    """
    if not text or not isinstance(text, str):
        logger.warning(f"Invalid input for JSON parsing: {type(text)}")
        return fallback_value or {"error": "Invalid input for JSON parsing"}
    
    # First, try to extract clean JSON
    cleaned_json = extract_json_from_text(text)
    if not cleaned_json:
        logger.warning("No JSON-like content found in text")
        return fallback_value or {"error": "No JSON content found", "raw_text": text[:200]}
    
    # Try standard JSON parsing
    try:
        return json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        logger.warning(f"Standard JSON parsing failed: {str(e)}")
    
    # Try fixing common JSON issues
    fixed_json = fix_common_json_issues(cleaned_json)
    if fixed_json != cleaned_json:
        try:
            result = json.loads(fixed_json)
            logger.info("Successfully parsed JSON after fixing common issues")
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed even after fixes: {str(e)}")
    
    # If all else fails, return error with original text for debugging
    logger.error(f"All JSON parsing strategies failed. Original text: {text[:500]}...")
    return fallback_value or {
        "error": "JSON parsing failed", 
        "raw_text": text[:500],
        "cleaned_json": cleaned_json[:500]
    }

def fix_common_json_issues(json_str: str) -> str:
    """
    Fix common JSON formatting issues that might come from AI responses.
    """
    # Fix trailing commas
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Fix single quotes to double quotes (but be careful with apostrophes)
    json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)  # Fix keys
    
    # Fix unescaped quotes in strings (basic attempt)
    # This is tricky and might not work in all cases
    json_str = re.sub(r':\s*"([^"]*)"([^"]*)"([^"]*)"', r': "\1\2\3"', json_str)
    
    return json_str

def create_fallback_response(error_message: str, raw_response: Any = None, include_raw: bool = True) -> Dict[str, Any]:
    """
    Create a standardized fallback response when JSON parsing fails.
    """
    result = {
        "error": error_message,
        "fallback_used": True,
        "parsing_failed": True
    }
    
    if include_raw and raw_response is not None:
        if isinstance(raw_response, str):
            result["raw_text"] = raw_response[:1000]  # Limit size
        else:
            result["raw_response"] = str(raw_response)[:1000]
    
    return result

def parse_gemini_response(gemini_response: Dict[str, Any], allow_partial: bool = True) -> Dict[str, Any]:
    """
    Parse a Gemini API response with flexible error handling.
    
    Args:
        gemini_response: The raw response from Gemini API
        allow_partial: If True, return partial data even if some parsing fails
    
    Returns:
        Parsed response or error information
    """
    # Check for basic response structure
    if not isinstance(gemini_response, dict):
        return create_fallback_response("Response is not a dictionary", gemini_response)
    
    if 'candidates' not in gemini_response:
        logger.warning("No candidates in Gemini response")
        return create_fallback_response("No candidates in response", gemini_response)
    
    candidates = gemini_response.get('candidates', [])
    if not candidates:
        # Check for safety blocking
        if 'promptFeedback' in gemini_response:
            feedback = gemini_response['promptFeedback']
            if 'blockReason' in feedback:
                error_msg = f"Content blocked: {feedback['blockReason']}"
            elif 'safetyRatings' in feedback:
                error_msg = f"Safety filtering applied: {feedback['safetyRatings']}"
            else:
                error_msg = "Content may have been filtered"
        else:
            error_msg = "No candidates in response"
        
        return create_fallback_response(error_msg, gemini_response)
    
    # Get the first candidate
    candidate = candidates[0]
    if 'content' not in candidate:
        return create_fallback_response("No content in candidate", candidate)
    
    content = candidate['content']
    if 'parts' not in content or not content['parts']:
        return create_fallback_response("No parts in content", content)
    
    # Extract text from the first part
    text = content['parts'][0].get('text', '').strip()
    if not text:
        return create_fallback_response("Empty response text", gemini_response)
    
    # Try to parse the text as JSON
    parsed_result = safe_json_parse(text)
    
    # If parsing failed but we allow partial results, include debug info
    if isinstance(parsed_result, dict) and parsed_result.get('error'):
        if allow_partial:
            parsed_result['gemini_raw_response'] = gemini_response
            parsed_result['gemini_text'] = text
        
        logger.warning(f"Gemini response parsing failed: {parsed_result.get('error')}")
    
    return parsed_result

def extract_text_from_gemini_response(gemini_response: Dict[str, Any]) -> Optional[str]:
    """
    Extract text content from a Gemini API response.
    Handles the standard candidates/content/parts structure.
    
    Args:
        gemini_response: The full response from Gemini API
    
    Returns:
        The extracted text content or None if extraction fails
    """
    try:
        if not isinstance(gemini_response, dict):
            logger.error(f"Invalid gemini_response type: {type(gemini_response)}")
            return None
        
        if 'candidates' not in gemini_response or not gemini_response['candidates']:
            logger.warning("No candidates in Gemini response")
            return None
        
        candidate = gemini_response['candidates'][0]
        if 'content' not in candidate:
            logger.warning("No content in Gemini candidate")
            return None
        
        content = candidate['content']
        if 'parts' not in content or not content['parts']:
            logger.warning("No parts in Gemini content")
            return None
        
        text = content['parts'][0].get('text', '').strip()
        return text if text else None
        
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Error extracting text from Gemini response: {str(e)}")
        return None
