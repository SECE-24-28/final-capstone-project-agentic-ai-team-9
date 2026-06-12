from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List

from mcp_server.tools.recommendation_tools import get_recommendations_tool
from mcp_server.tools.tmdb_tools import search_movies_tool
from services.tmdb import tmdb_service
from rag.pipeline import rag_pipeline
from db import database as db

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class RecommendRequest(BaseModel):
    user_id: str
    query: str = ""
    n: int = 12


# ── Search by movie name (TMDB live search) ──────────────────────────────────
@router.get("/search")
async def search_movies(q: str = Query(..., min_length=1)):
    """Search TMDB for movies matching a title/keyword query."""
    movies = search_movies_tool(q)
    return {"results": movies, "count": len(movies)}


# ── Trending ─────────────────────────────────────────────────────────────────
@router.get("/trending/now")
async def get_trending():
    movies = tmdb_service.get_trending("week")
    return {"trending": movies}


# ── DNA-powered generation ───────────────────────────────────────────────────
@router.post("/generate")
async def generate_recommendations(req: RecommendRequest):
    # If no explicit query, auto-build one from the user's DNA profile
    query = req.query
    if not query:
        profile = db.get_profile(req.user_id) or {}
        parts = []
        if profile.get("favorite_genres"):
            parts.append(" ".join(profile["favorite_genres"]))
        if profile.get("favorite_movies"):
            parts.append(" ".join(profile["favorite_movies"][:3]))
        if profile.get("hidden_taste"):
            parts.append(profile["hidden_taste"][:80])
        query = " ".join(parts)

    movies = get_recommendations_tool(req.user_id, query, req.n)
    for movie in movies:
        rag_pipeline.index_movie(movie)
    return {"user_id": req.user_id, "recommendations": movies, "count": len(movies)}


# ── Get saved recommendations (history) ──────────────────────────────────────
@router.get("/{user_id}")
async def get_recommendations(user_id: str, n: int = 12):
    # Try history first
    history = db.get_recommendation_history(user_id, limit=n)
    if history:
        enriched: List[dict] = []
        for h in history:
            movie_id = h.get("movie_id")
            if movie_id:
                try:
                    details = tmdb_service.get_movie_details(int(movie_id))
                    details["reason"] = h.get("reason", "")
                    enriched.append(details)
                    continue
                except Exception:
                    pass
            enriched.append({
                "id": movie_id,
                "title": h.get("movie_title", ""),
                "overview": "",
                "poster_path": None,
                "vote_average": 0,
                "reason": h.get("reason", ""),
            })
        return {"recommendations": enriched}

    # No history — show trending as default
    movies = tmdb_service.get_trending("week")[:n]
    return {"recommendations": movies}


@router.post("/rate")
async def rate_movie(user_id: str, movie_id: int, movie_title: str, rating: float, review: str = ""):
    if rating < 0 or rating > 10:
        raise HTTPException(status_code=400, detail="Rating must be 0-10")
    db.add_rating(user_id, movie_id, movie_title, rating, review)
    return {"message": "Rating saved"}

