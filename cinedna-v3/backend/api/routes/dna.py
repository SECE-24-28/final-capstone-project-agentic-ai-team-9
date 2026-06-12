from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from services.dna_profiler import dna_profiler
from rag.pipeline import rag_pipeline
from db import database as db

router = APIRouter(prefix="/api/dna", tags=["dna"])


class DNARequest(BaseModel):
    user_id: str
    favorite_movies: List[str]
    favorite_characters: List[str]
    favorite_genres: List[str]


@router.post("/generate")
async def generate_dna(req: DNARequest):
    db.ensure_user(req.user_id)

    # Generate DNA via LLM
    dna = dna_profiler.generate_full_dna({
        "favorite_movies": req.favorite_movies,
        "favorite_characters": req.favorite_characters,
        "favorite_genres": req.favorite_genres,
    })

    # Save to SQLite
    db.update_profile(req.user_id, {
        "favorite_movies": req.favorite_movies,
        "favorite_characters": req.favorite_characters,
        "favorite_genres": req.favorite_genres,
        **dna,
    })

    # Index into ChromaDB
    profile = db.get_profile(req.user_id)
    rag_pipeline.index_user_profile(req.user_id, profile)

    return {"user_id": req.user_id, "dna": dna, "profile": profile}


@router.get("/{user_id}")
async def get_dna(user_id: str):
    profile = db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/regenerate/{user_id}")
async def regenerate_dna(user_id: str):
    profile = db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    dna = dna_profiler.generate_full_dna(profile)
    db.update_profile(user_id, dna)
    rag_pipeline.index_user_profile(user_id, db.get_profile(user_id))
    return {"user_id": user_id, "dna": dna}
