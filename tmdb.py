"""
CineDNA – TMDB API integration + LangChain Tool wrapper (Phase 6).
"""

import os
import time
import logging
import requests
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CineDNA.TMDB")

_session = requests.Session()
_session.headers.update({
    "Authorization": f"Bearer {TMDB_API_KEY}",
    "accept": "application/json"
})


# --------------------------------------------------------------------------- #
#  Core TMDB functions                                                        #
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=128)
def search_movie(query: str) -> tuple:
    """Search for a movie by title. Cached."""
    if not TMDB_API_KEY:
        return ()
    start = time.time()
    try:
        r = _session.get(f"{BASE_URL}/search/movie",
                         params={"query": query, "language": "en-US", "page": 1},
                         timeout=5)
        logger.info("TMDB search '%s': %.2fs | status=%d", query, time.time()-start, r.status_code)
        if r.status_code == 200:
            return tuple(
                {
                    "id":           m["id"],
                    "title":        m["title"],
                    "release_date": m.get("release_date", ""),
                    "overview":     m.get("overview", "")[:200],
                    "vote_average": m.get("vote_average", 0),
                    "poster_path":  m.get("poster_path", ""),
                    "poster_url":   f"{IMG_BASE}{m['poster_path']}" if m.get("poster_path") else "",
                }
                for m in r.json().get("results", [])[:5]
            )
    except requests.Timeout:
        logger.warning("TMDB timeout: %s", query)
    except Exception as e:
        logger.error("TMDB search error: %s", e)
    return ()


@lru_cache(maxsize=64)
def get_movie_details(movie_id: int) -> Optional[dict]:
    """Get full movie details including cast. Cached."""
    if not TMDB_API_KEY:
        return None
    start = time.time()
    try:
        r = _session.get(f"{BASE_URL}/movie/{movie_id}", timeout=5)
        logger.info("TMDB details %d: %.2fs", movie_id, time.time()-start)
        if r.status_code == 200:
            m = r.json()
            # Fetch credits in parallel-ish
            cast = _get_cast(movie_id)
            return {
                "id":           m["id"],
                "title":        m["title"],
                "release_date": m.get("release_date", ""),
                "overview":     m.get("overview", ""),
                "vote_average": m.get("vote_average", 0),
                "genres":       [g["name"] for g in m.get("genres", [])],
                "runtime":      m.get("runtime", 0),
                "poster_path":  m.get("poster_path", ""),
                "poster_url":   f"{IMG_BASE}{m['poster_path']}" if m.get("poster_path") else "",
                "cast":         cast,
            }
    except Exception as e:
        logger.error("TMDB details error: %s", e)
    return None


@lru_cache(maxsize=64)
def _get_cast(movie_id: int) -> list:
    try:
        r = _session.get(f"{BASE_URL}/movie/{movie_id}/credits", timeout=5)
        if r.status_code == 200:
            return [
                {"name": c["name"], "character": c.get("character", "")}
                for c in r.json().get("cast", [])[:5]
            ]
    except Exception:
        pass
    return []


@lru_cache(maxsize=64)
def get_movie_recommendations(movie_id: int) -> tuple:
    """Get TMDB-powered similar movies. Cached."""
    if not TMDB_API_KEY:
        return ()
    try:
        r = _session.get(f"{BASE_URL}/movie/{movie_id}/recommendations",
                         params={"language": "en-US", "page": 1}, timeout=5)
        if r.status_code == 200:
            return tuple(
                {
                    "id":           m["id"],
                    "title":        m["title"],
                    "release_date": m.get("release_date", ""),
                    "overview":     m.get("overview", "")[:150],
                    "vote_average": m.get("vote_average", 0),
                    "poster_url":   f"{IMG_BASE}{m['poster_path']}" if m.get("poster_path") else "",
                }
                for m in r.json().get("results", [])[:5]
            )
    except Exception as e:
        logger.error("TMDB recommendations error: %s", e)
    return ()


# --------------------------------------------------------------------------- #
#  Phase 6: LangChain Tool wrapper                                            #
# --------------------------------------------------------------------------- #
def tmdb_search_tool(query: str) -> str:
    """
    LangChain-compatible TMDB search tool.
    Input: movie title string.
    Output: formatted string with movie info (title, year, rating, overview).
    """
    results = search_movie(query)
    if not results:
        return f"No TMDB results found for '{query}'."

    lines = [f"TMDB results for '{query}':"]
    for m in list(results)[:3]:
        year = m["release_date"][:4] if m.get("release_date") else "N/A"
        lines.append(
            f"• {m['title']} ({year}) | Rating: {m['vote_average']:.1f}/10\n"
            f"  {m['overview'][:120]}..."
        )
    return "\n".join(lines)


def tmdb_details_tool(movie_title: str) -> str:
    """
    LangChain-compatible TMDB details tool.
    Searches for the movie then fetches full details + cast.
    """
    results = search_movie(movie_title)
    if not results:
        return f"Could not find '{movie_title}' on TMDB."

    details = get_movie_details(results[0]["id"])
    if not details:
        return f"Could not retrieve details for '{movie_title}'."

    year  = details["release_date"][:4] if details.get("release_date") else "N/A"
    genres = ", ".join(details["genres"]) if details.get("genres") else "N/A"
    cast  = ", ".join(f"{c['name']} as {c['character']}"
                      for c in details.get("cast", [])[:3]) or "N/A"
    return (
        f"**{details['title']}** ({year})\n"
        f"Rating: {details['vote_average']:.1f}/10 | Runtime: {details.get('runtime',0)} min\n"
        f"Genres: {genres}\n"
        f"Cast: {cast}\n"
        f"Overview: {details['overview'][:200]}..."
    )


def clear_cache():
    search_movie.cache_clear()
    get_movie_details.cache_clear()
    get_movie_recommendations.cache_clear()
    _get_cast.cache_clear()
    logger.info("TMDB cache cleared")
