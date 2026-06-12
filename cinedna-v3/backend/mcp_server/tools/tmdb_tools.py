from typing import List, Dict
from services.tmdb import tmdb_service


def search_movies_tool(query: str, page: int = 1) -> List[Dict]:
    """Search TMDB for movies by keyword query."""
    return tmdb_service.search_movies(query, page=page)


def get_movie_details_tool(movie_id: int) -> Dict:
    """Get detailed info about a movie by TMDB ID."""
    return tmdb_service.get_movie_details(movie_id)


def get_trending_movies_tool(time_window: str = "week") -> List[Dict]:
    """Get trending movies from TMDB."""
    return tmdb_service.get_trending(time_window)


def get_similar_movies_tool(movie_id: int) -> List[Dict]:
    """Get movies similar to a given TMDB movie ID."""
    return tmdb_service.get_similar(movie_id)
