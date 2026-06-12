from typing import Dict, Any
from db import database as db


def get_user_profile_tool(user_id: str) -> Dict[str, Any]:
    """Fetch a user's full DNA profile from SQLite."""
    return db.get_profile(user_id) or {}


def get_ratings_tool(user_id: str) -> list:
    """Fetch a user's movie ratings."""
    return db.get_ratings(user_id)
