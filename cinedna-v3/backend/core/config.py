from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "CineDNA V3"
    APP_VERSION: str = "3.0.0"
    DEBUG: bool = True

    # TMDB — Bearer JWT token
    TMDB_API_KEY: str = ""
    TMDB_BASE_URL: str = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL: str = "https://image.tmdb.org/t/p/w500"

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:1.7b"

    # SQLite
    DB_PATH: str = "cinedna.db"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
