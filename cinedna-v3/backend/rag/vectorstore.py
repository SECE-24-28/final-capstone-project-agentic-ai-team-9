import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Optional

from core.config import settings
from rag.embeddings import embeddings


class VectorStore:
    """ChromaDB vector store with collections for movies and user prefs."""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.movies = self.client.get_or_create_collection(
            name="movies",
            metadata={"hnsw:space": "cosine"},
        )
        self.user_prefs = self.client.get_or_create_collection(
            name="user_preferences",
            metadata={"hnsw:space": "cosine"},
        )
        self.rec_history = self.client.get_or_create_collection(
            name="recommendation_history",
            metadata={"hnsw:space": "cosine"},
        )

    # ─── Movies ──────────────────────────────────────────────────────────────

    def upsert_movie(self, movie: Dict):
        """Embed and store a movie document."""
        doc = (
            f"{movie.get('title', '')}. "
            f"{movie.get('overview', '')} "
            f"Genres: {movie.get('genre_ids', [])}. "
            f"Rating: {movie.get('vote_average', 0)}."
        )
        emb = embeddings.embed(doc)
        self.movies.upsert(
            ids=[str(movie["id"])],
            documents=[doc],
            embeddings=[emb],
            metadatas=[{
                "title": movie.get("title", ""),
                "movie_id": str(movie.get("id", "")),
                "vote_average": float(movie.get("vote_average", 0)),
                "poster_path": movie.get("poster_path") or "",
            }],
        )

    def search_movies(self, query: str, n: int = 10) -> List[Dict]:
        if self.movies.count() == 0:
            return []
        emb = embeddings.embed(query)
        results = self.movies.query(
            query_embeddings=[emb],
            n_results=min(n, self.movies.count()),
            include=["documents", "metadatas", "distances"],
        )
        items = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            items.append({**meta, "relevance_score": 1 - dist, "overview": doc})
        return items

    # ─── User Prefs ───────────────────────────────────────────────────────────

    def upsert_user_preference(self, user_id: str, preference_text: str):
        emb = embeddings.embed(preference_text)
        self.user_prefs.upsert(
            ids=[user_id],
            documents=[preference_text],
            embeddings=[emb],
            metadatas=[{"user_id": user_id}],
        )

    def search_user_similar(self, query: str, n: int = 5) -> List[Dict]:
        if self.user_prefs.count() == 0:
            return []
        emb = embeddings.embed(query)
        results = self.user_prefs.query(
            query_embeddings=[emb],
            n_results=min(n, self.user_prefs.count()),
            include=["documents", "metadatas"],
        )
        return [
            {"user_id": m["user_id"], "preference": d}
            for d, m in zip(results["documents"][0], results["metadatas"][0])
        ]

    # ─── Rec History ──────────────────────────────────────────────────────────

    def upsert_recommendation(self, rec_id: str, user_id: str, title: str, reason: str):
        doc = f"{title}: {reason}"
        emb = embeddings.embed(doc)
        self.rec_history.upsert(
            ids=[rec_id],
            documents=[doc],
            embeddings=[emb],
            metadatas=[{"user_id": user_id, "title": title}],
        )


vector_store = VectorStore()
