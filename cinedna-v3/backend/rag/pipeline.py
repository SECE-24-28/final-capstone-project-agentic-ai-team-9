from typing import List, Dict, Any

from rag.embeddings import embeddings
from rag.vectorstore import vector_store
from services.tmdb import tmdb_service
from db import database as db


class RAGPipeline:
    """
    Query → Embed → ChromaDB → TMDB Enrich → Qwen Context
    """

    def build_context(self, user_id: str, query: str) -> str:
        """Build RAG context string for the LLM."""
        profile = db.get_profile(user_id) or {}
        ratings = db.get_ratings(user_id)
        history = db.get_recommendation_history(user_id)

        # Vector search for relevant movies
        similar_movies = vector_store.search_movies(query, n=5)

        # Build context block
        parts = []

        if profile.get("soul_profile"):
            parts.append(f"USER SOUL PROFILE: {profile['soul_profile']}")
        if profile.get("character_dna"):
            parts.append(f"CHARACTER DNA: {profile['character_dna']}")
        if profile.get("hidden_taste"):
            parts.append(f"HIDDEN TASTE: {profile['hidden_taste']}")
        if profile.get("favorite_movies"):
            parts.append(f"FAVORITE MOVIES: {', '.join(profile['favorite_movies'])}")
        if profile.get("favorite_genres"):
            parts.append(f"FAVORITE GENRES: {', '.join(profile['favorite_genres'])}")

        if ratings:
            recent = ratings[:5]
            rating_str = ", ".join(
                f"{r['movie_title']} ({r['rating']}/10)" for r in recent
            )
            parts.append(f"RECENT RATINGS: {rating_str}")

        if similar_movies:
            movie_str = "; ".join(
                f"{m['title']} (score: {m.get('relevance_score', 0):.2f})"
                for m in similar_movies
            )
            parts.append(f"RELATED MOVIES IN KNOWLEDGE BASE: {movie_str}")

        if history:
            past = [h["movie_title"] for h in history[:5]]
            parts.append(f"PREVIOUSLY RECOMMENDED: {', '.join(past)}")

        return "\n".join(parts)

    def index_movie(self, movie: Dict):
        """Index a movie into ChromaDB."""
        vector_store.upsert_movie(movie)

    def index_user_profile(self, user_id: str, profile: Dict):
        """Index user preferences into ChromaDB."""
        pref_text = (
            f"Favorite movies: {', '.join(profile.get('favorite_movies', []))}. "
            f"Favorite genres: {', '.join(profile.get('favorite_genres', []))}. "
            f"Favorite characters: {', '.join(profile.get('favorite_characters', []))}. "
            f"Soul profile: {profile.get('soul_profile', '')}."
        )
        vector_store.upsert_user_preference(user_id, pref_text)

    def hybrid_recommend(self, user_id: str, query: str = "", n: int = 10) -> List[Dict]:
        """Hybrid: vector search + TMDB trending."""
        profile = db.get_profile(user_id) or {}
        history_ids = {
            h["movie_id"] for h in db.get_recommendation_history(user_id)
        }

        # Build preference query
        pref_query = query or (
            f"{' '.join(profile.get('favorite_genres', []))} "
            f"{' '.join(profile.get('favorite_movies', []))}"
        ).strip()

        # Vector search — results use 'movie_id' key; normalise to 'id'
        raw_vector = vector_store.search_movies(pref_query, n=n) if pref_query else []
        vector_results = []
        for m in raw_vector:
            mid = m.get("id") or m.get("movie_id", "")
            try:
                mid_int = int(mid)
            except (ValueError, TypeError):
                continue
            # Enrich with TMDB if poster is missing
            if not m.get("poster_path"):
                try:
                    enriched = tmdb_service.get_movie_details(mid_int)
                    enriched["relevance_score"] = m.get("relevance_score", 1.0)
                    vector_results.append(enriched)
                    continue
                except Exception:
                    pass
            m["id"] = mid_int
            vector_results.append(m)

        # TMDB trending fallback
        tmdb_results = tmdb_service.get_trending()

        # Merge and deduplicate
        seen = set()
        merged = []
        for m in vector_results + tmdb_results:
            mid = str(m.get("id") or m.get("movie_id", ""))
            if not mid:
                continue
            try:
                mid_int = int(mid)
            except (ValueError, TypeError):
                continue
            if mid not in seen and mid_int not in history_ids:
                seen.add(mid)
                merged.append(m)
            if len(merged) >= n:
                break

        return merged


rag_pipeline = RAGPipeline()
