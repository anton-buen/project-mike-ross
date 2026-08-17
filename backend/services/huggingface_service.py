import json
import re
import os
import time
import requests
from fastapi import HTTPException

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
TEXT_MODEL = os.getenv("HF_TEXT_MODEL_ID")
VISION_MODEL = os.getenv("HF_VISION_MODEL_ID")

def call_huggingface_api(model_id: str, payload: dict, is_retry: bool = False) -> dict:
    """
    Makes a POST request to the Hugging Face Inference API.
    Implements Section 7.3 with automatic cold-start retry.
    """
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=20)
    
    if response.status_code == 503 and not is_retry:
        error_data = response.json()
        wait_time = error_data.get("estimated_time", 10.0)
        time.sleep(wait_time)
        
        return call_huggingface_api(model_id, payload, is_retry=True)
        
    # If it fails for any other reason, or fails on the retry, raise a 502 error
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="HF_API_ERROR")
        
    return response.json()

def extract_text_from_image(base64_image: str) -> str:
    """
    Stage A: Extracts raw text from a screenshot.
    Implements Section 7.2 (Stage A).
    """
    payload = {"inputs": base64_image}
    
    # Using the vision model 
    response = call_huggingface_api(VISION_MODEL, payload)
    
    if isinstance(response, list) and len(response) > 0:
        return response[0].get("generated_text", "")
    return ""

def parse_structured(prompt: str) -> dict:
    """
    Stage B: Sends the system prompt to the text model and parses the JSON response.
    Implements Section 7.2 (Stage B).
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "return_full_text": False,
            "temperature": 0.1  # deterministic
        }
    }
    
    response = call_huggingface_api(TEXT_MODEL, payload)
    
    if isinstance(response, list) and len(response) > 0:
        raw_output = response[0].get("generated_text", "")
    else:
        raw_output = ""
        
    return clean_and_parse_json(raw_output)

def clean_and_parse_json(raw_text: str) -> dict:
    """
    Post-processes the AI output to extract valid JSON.
    Implements Section 7.5.
    """
    cleaned = re.sub(r"```json\s*", "", raw_text)
    cleaned = re.sub(r"```\s*", "", cleaned)
    
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
                
    return {
        "item_type": "unknown",
        "confidence": 0.0,
        "reasoning": "Failed to parse JSON from AI response."
    }