from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json

from llm.agent import agent
from db import database as db

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    user_id: str
    message: str
    stream: bool = True


class HistoryRequest(BaseModel):
    user_id: str
    limit: int = 20


@router.post("")
async def chat(req: ChatRequest):
    if req.stream:
        async def event_stream():
            async for token in agent.stream_chat(
                req.user_id, req.message,
                db.get_chat_history(req.user_id, limit=10)
            ):
                yield f"data: {json.dumps({'token': token})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    response = agent.chat(
        req.user_id, req.message,
        db.get_chat_history(req.user_id, limit=10)
    )
    return {"response": response}


@router.get("/history/{user_id}")
async def get_history(user_id: str, limit: int = 20):
    return {"history": db.get_chat_history(user_id, limit=limit)}


@router.delete("/history/{user_id}")
async def clear_history(user_id: str):
    db.clear_chat_history(user_id)
    return {"message": "Chat history cleared"}
