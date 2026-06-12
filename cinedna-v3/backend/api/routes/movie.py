from fastapi import APIRouter, HTTPException
from services.tmdb import tmdb_service

router = APIRouter(prefix="/api/movie", tags=["movie"])


@router.get("/{movie_id}")
async def get_movie_detail(movie_id: int):
    """Get full TMDB details for a single movie including cast, director, genres."""
    try:
        movie = tmdb_service.get_movie_details(movie_id)
        return movie
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Movie not found: {e}")
