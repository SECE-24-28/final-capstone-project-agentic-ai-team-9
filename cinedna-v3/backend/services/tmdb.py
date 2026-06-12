import requests
from typing import Optional, Dict, Any, List
from functools import lru_cache

from core.config import settings
from services.cache import cache


class TMDBService:
    """TMDB API client using Bearer JWT token."""

    def __init__(self):
        self.base_url = settings.TMDB_BASE_URL
        self.image_base = settings.TMDB_IMAGE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {settings.TMDB_API_KEY}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        cache_key = f"tmdb:{path}:{str(params)}"
        cached = cache.get(cache_key)
        if cached:
            return cached
        resp = requests.get(
            f"{self.base_url}{path}",
            headers=self.headers,
            params=params or {},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        cache.set(cache_key, data, ttl=3600)
        return data

    def search_movies(self, query: str, page: int = 1) -> List[Dict]:
        data = self._get("/search/movie", {"query": query, "page": page})
        return [self._format_movie(m) for m in data.get("results", [])]

    def get_movie_details(self, movie_id: int) -> Dict:
        data = self._get(f"/movie/{movie_id}", {"append_to_response": "credits,keywords"})
        return self._format_movie(data, detailed=True)

    def get_trending(self, time_window: str = "week") -> List[Dict]:
        data = self._get(f"/trending/movie/{time_window}")
        return [self._format_movie(m) for m in data.get("results", [])]

    def get_similar(self, movie_id: int) -> List[Dict]:
        data = self._get(f"/movie/{movie_id}/similar")
        return [self._format_movie(m) for m in data.get("results", [])]

    def get_by_genre(self, genre_ids: List[int], page: int = 1) -> List[Dict]:
        data = self._get("/discover/movie", {
            "with_genres": ",".join(str(g) for g in genre_ids),
            "sort_by": "popularity.desc",
            "page": page,
        })
        return [self._format_movie(m) for m in data.get("results", [])]

    def get_genres(self) -> List[Dict]:
        data = self._get("/genre/movie/list")
        return data.get("genres", [])

    def _format_movie(self, m: Dict, detailed: bool = False) -> Dict:
        result = {
            "id": m.get("id"),
            "title": m.get("title", ""),
            "overview": m.get("overview", ""),
            "release_date": m.get("release_date", ""),
            "vote_average": m.get("vote_average", 0),
            "popularity": m.get("popularity", 0),
            "genre_ids": m.get("genre_ids", []),
            "poster_path": (
                f"{self.image_base}{m['poster_path']}"
                if m.get("poster_path") else None
            ),
            "backdrop_path": (
                f"{self.image_base}{m['backdrop_path']}"
                if m.get("backdrop_path") else None
            ),
        }
        if detailed:
            credits = m.get("credits", {})
            result["cast"] = [
                {"name": a["name"], "character": a["character"]}
                for a in credits.get("cast", [])[:10]
            ]
            result["director"] = next(
                (c["name"] for c in credits.get("crew", []) if c["job"] == "Director"),
                None,
            )
            result["keywords"] = [
                k["name"] for k in m.get("keywords", {}).get("keywords", [])
            ]
            result["genres"] = m.get("genres", [])
        return result


tmdb_service = TMDBService()
