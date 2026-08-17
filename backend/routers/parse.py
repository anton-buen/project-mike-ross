import uuid
import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from services.huggingface_service import extract_text_from_image, parse_structured
from logic.parsing_logic import infer_priority_fallback
from db.database import get_db_connection

router = APIRouter()

class ParseContext(BaseModel):
    current_url: Optional[str] = None
    user_timezone: Optional[str] = "UTC"
    default_priority: Optional[str] = "medium"
    default_tags: Optional[List[str]] = []

class ParseRequest(BaseModel):
    input_type: str  # "screenshot", "voice", or "text"
    input_data: str  # Base64 string or plain text
    context: Optional[ParseContext] = ParseContext()

@router.post("/api/parse")
def parse_capture(request: ParseRequest):
    """
    Accepts a screenshot, voice transcript, or text and will return structured task/event data.
    """
    valid_types = ["screenshot", "voice", "text"]
    if request.input_type not in valid_types:
        raise HTTPException(status_code=400, detail="INVALID_INPUT_TYPE")
    
    if not request.input_data.strip():
        raise HTTPException(status_code=400, detail="EMPTY_INPUT")

    # TODO: Add rate limiting, Hugging Face AI extraction, and DB persistence later.
    
    # Temporary stub response matching the Section 6 success envelope
    return {
        "success": True,
        "data": {
            "item_type": "unknown",
            "title": "Stubbed parsing endpoint",
            "confidence": 0.0
        },
        "error": None,
        "request_id": "stub-uuid-1234"
    }

def build_system_prompt(extracted_text: str, current_date: str, user_timezone: str) -> str:
    """
    Constructs the rigid instruction prompt for the Hugging Face model.
    Implements Section 7.4.
    """
    return f"""ROLE: You are a task and event extraction system.

INSTRUCTIONS:
1. Read the input text below.
2. Classify it as exactly one of: "task", "event", or "unknown".
3. Extract fields exactly matching this JSON schema. Output ONLY the JSON object, no markdown formatting.

SCHEMA:
{{
  "item_type": "task" | "event" | "unknown",
  "title": "string (max 60 chars)",
  "description": "string or null",
  "priority": "low" | "medium" | "high",
  "due_date": "YYYY-MM-DD or null",
  "due_time": "HH:MM or null",
  "duration_minutes": "integer or null",
  "tags": ["array of strings"],
  "subtasks": ["array of strings"],
  "assignee": "string or null",
  "confidence": "float 0.0-1.0",
  "reasoning": "string"
}}

CURRENT_DATE: {current_date}
USER_TIMEZONE: {user_timezone}

INPUT TEXT:
{extracted_text}"""

def save_capture_to_db(capture_id: str, input_type: str, parsed_data: dict):
    """
    Saves the parsed capture to the SQLite database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO captures (
            id, capture_type, item_type, title, description, priority, 
            due_date, due_time, confidence, reasoning
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        capture_id,
        input_type,
        parsed_data.get("item_type", "unknown"),
        parsed_data.get("title", "Untitled Capture"),
        parsed_data.get("description"),
        parsed_data.get("priority", "medium"),
        parsed_data.get("due_date"),
        parsed_data.get("due_time"),
        float(parsed_data.get("confidence", 0.0)),
        parsed_data.get("reasoning", "")
    ))
    
    conn.commit()
    conn.close()