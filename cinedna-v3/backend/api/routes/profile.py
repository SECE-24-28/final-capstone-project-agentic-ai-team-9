from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from db import database as db
from mcp_server.tools.taste_tools import analyze_and_save_evolution_tool

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    favorite_movies: Optional[List[str]] = None
    favorite_characters: Optional[List[str]] = None
    favorite_genres: Optional[List[str]] = None


class RatingRequest(BaseModel):
    movie_id: int
    movie_title: str
    rating: float
    review: str = ""


@router.get("/{user_id}")
async def get_profile(user_id: str):
    profile = db.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{user_id}")
async def update_profile(user_id: str, data: ProfileUpdate):
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    db.update_profile(user_id, update_data)
    return db.get_profile(user_id)


@router.post("/{user_id}/rate")
async def rate_movie(user_id: str, req: RatingRequest):
    if req.rating < 0 or req.rating > 10:
        raise HTTPException(status_code=400, detail="Rating must be between 0 and 10")
    db.add_rating(user_id, req.movie_id, req.movie_title, req.rating, req.review)
    return {"message": "Rating saved successfully"}


@router.get("/{user_id}/ratings")
async def get_ratings(user_id: str):
    return {"ratings": db.get_ratings(user_id)}


@router.get("/{user_id}/evolution")
async def get_taste_evolution(user_id: str):
    return {"evolution": db.get_taste_evolution(user_id)}


@router.post("/{user_id}/evolution/analyze")
async def analyze_evolution(user_id: str):
    analysis = analyze_and_save_evolution_tool(user_id)
    return {"analysis": analysis}
