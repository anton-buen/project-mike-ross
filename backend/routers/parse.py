from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

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