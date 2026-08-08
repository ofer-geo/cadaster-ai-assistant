from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent.assistant import CadasterAssistant
from backend.database.repository import get_current_parcels_geojson
from typing import Any
import os


app = FastAPI(
    title="Cadaster AI Assistant API",
    version="1.0.0",
)

# React currently runs on this address.
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

assistant = CadasterAssistant()


class ChatRequest(BaseModel):
    message: str
    thread_id: str


class ChatResponse(BaseModel):
    answer: str
    thread_id: str
    parcel_version_ids: list[int]
    geojson: dict[str, Any]


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Cadaster AI Assistant API is running."
    }

@app.get("/parcels/current/geojson")
def current_parcels_geojson() -> dict:
    try:
        return get_current_parcels_geojson()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not load current parcels.",
        ) from exc


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        result = assistant.chat(
            message=request.message,
            thread_id=request.thread_id,
        )

        return ChatResponse(
            answer=result.answer,
            thread_id=result.thread_id,
            parcel_version_ids=result.parcel_version_ids,
            geojson=result.geojson,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="The assistant could not process the request.",
        ) from exc


@app.get("/health")
def health_check():
    return {"status": "ok"}