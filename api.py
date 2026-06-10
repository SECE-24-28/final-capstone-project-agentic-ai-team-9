from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

from llm import generate_full_profile, get_movie_chat_response
from database import get_user_profile, save_user_preferences, get_recent_messages, save_message

app = FastAPI(title="CineDNA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DNARequest(BaseModel):
    movies: str
    characters: str
    genres: str

class ChatRequest(BaseModel):
    user_id: str
    query: str
    profile: dict

@app.post("/api/generate-dna")
async def api_generate_dna(req: DNARequest):
    try:
        results = generate_full_profile(req.movies, req.characters, req.genres)
        return {
            "soul_profile": results["soul_profile"],
            "character_dna": results["character_dna"],
            "hidden_taste": results["hidden_taste"],
            "favorite_movies": req.movies,
            "favorite_characters": req.characters,
            "favorite_genres": req.genres
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    try:
        history = get_recent_messages(req.user_id, limit=8)
        
        # We collect the full generator into a string for this simple API endpoint
        # In a full production app, this would use StreamingResponse
        stream = get_movie_chat_response(
            user_input=req.query,
            chat_history=history,
            user_profile=req.profile,
            stream=False
        )
        
        full_reply = "".join(list(stream))
        
        save_message(req.user_id, "user", req.query)
        save_message(req.user_id, "assistant", full_reply)
        
        return {"reply": full_reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
