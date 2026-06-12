"""
CineDNA MCP Server — exposes 5 tools via FastMCP (SSE transport).
The LangChain agent uses these same tool functions directly as LangChain tools.
External MCP clients (e.g. Claude Desktop) can connect via /mcp/sse.
"""
from mcp.server.fastmcp import FastMCP

from mcp_server.tools.tmdb_tools import (
    search_movies_tool,
    get_movie_details_tool,
    get_trending_movies_tool,
    get_similar_movies_tool,
)
from mcp_server.tools.recommendation_tools import get_recommendations_tool
from mcp_server.tools.profile_tools import get_user_profile_tool, get_ratings_tool
from mcp_server.tools.taste_tools import (
    get_taste_evolution_tool,
    analyze_and_save_evolution_tool,
)

mcp = FastMCP("CineDNA")


@mcp.tool()
def search_movies(query: str, page: int = 1) -> list:
    """Search TMDB for movies matching a keyword query."""
    return search_movies_tool(query, page)


@mcp.tool()
def get_movie_details(movie_id: int) -> dict:
    """Get detailed movie info including cast, director, keywords."""
    return get_movie_details_tool(movie_id)


@mcp.tool()
def get_trending_movies(time_window: str = "week") -> list:
    """Get trending movies from TMDB (day or week)."""
    return get_trending_movies_tool(time_window)


@mcp.tool()
def get_similar_movies(movie_id: int) -> list:
    """Get movies similar to a given TMDB movie ID."""
    return get_similar_movies_tool(movie_id)


@mcp.tool()
def get_recommendations(user_id: str, query: str = "", n: int = 10) -> list:
    """Generate hybrid movie recommendations for a user based on their DNA."""
    return get_recommendations_tool(user_id, query, n)


@mcp.tool()
def get_user_profile(user_id: str) -> dict:
    """Fetch a user's full CineDNA profile."""
    return get_user_profile_tool(user_id)


@mcp.tool()
def get_user_ratings(user_id: str) -> list:
    """Get all movie ratings for a user."""
    return get_ratings_tool(user_id)


@mcp.tool()
def get_taste_evolution(user_id: str) -> list:
    """Get the taste evolution history for a user."""
    return get_taste_evolution_tool(user_id)


@mcp.tool()
def analyze_taste_evolution(user_id: str) -> str:
    """Analyze and persist a new taste evolution snapshot for a user."""
    return analyze_and_save_evolution_tool(user_id)
