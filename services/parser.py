import json
import re


def parse_json(response):
    """
    Parse the response from the MedGemma API.
    Handles both dict (already parsed JSON) and raw string responses.
    """

    # If it's already a dict (API returned parsed JSON), return as-is
    if isinstance(response, dict):
        return response

    if not isinstance(response, str):
        return {"error": True, "message": "Unexpected response type", "raw": str(response)}

    # Try direct JSON parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON block from markdown code fences
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding any JSON object in the string
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Last resort: return raw text in a structured envelope
    return {
        "error": True,
        "message": "Could not parse structured JSON from model response.",
        "raw_output": response
    }