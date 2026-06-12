from typing import List, Dict
from db import database as db
from rag.pipeline import rag_pipeline


def get_recommendations_tool(user_id: str, query: str = "", n: int = 10) -> List[Dict]:
    """Generate hybrid movie recommendations for a user."""
    movies = rag_pipeline.hybrid_recommend(user_id, query=query, n=n)
    for movie in movies:
        db.add_recommendation(
            user_id,
            movie.get("id", 0),
            movie.get("title", ""),
            reason=f"Matched your DNA profile via hybrid search."
        )
    return movies
