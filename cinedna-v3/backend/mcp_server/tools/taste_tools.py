from typing import Dict, Any, List
from db import database as db
from services.dna_profiler import dna_profiler


def get_taste_evolution_tool(user_id: str) -> List[Dict]:
    """Get the taste evolution history for a user."""
    return db.get_taste_evolution(user_id)


def analyze_and_save_evolution_tool(user_id: str) -> str:
    """Analyze taste evolution and persist snapshot."""
    ratings = db.get_ratings(user_id)
    history = db.get_recommendation_history(user_id)
    analysis = dna_profiler.analyze_taste_evolution(ratings, history)
    profile = db.get_profile(user_id) or {}
    snapshot = {
        "favorite_movies": profile.get("favorite_movies", []),
        "favorite_genres": profile.get("favorite_genres", []),
        "recent_ratings": [
            {"title": r["movie_title"], "rating": r["rating"]} for r in ratings[:5]
        ],
    }
    db.add_taste_snapshot(user_id, snapshot, analysis)
    return analysis
