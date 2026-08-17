import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Project Mike Ross API")

allowed_origin = os.getenv("CORS_ALLOWED_ORIGIN", "")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "success": True,
        "data": {"status": "ok", "version": "2.0.0"},
        "error": None,
        "request_id": "init"
    }