"""
LangChain-powered CineDNA Agent using Qwen3 via Ollama.
Uses direct ChatOllama with tool-augmented prompting for compatibility
with the latest LangChain release.
"""
import json
from typing import AsyncIterator, List, Dict
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from core.config import settings
from rag.pipeline import rag_pipeline
from db import database as db

# ─── Tool imports (shared with MCP server) ───────────────────────────────────
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


# ─── LangChain Tool Wrappers ─────────────────────────────────────────────────

@tool
def search_movies(query: str) -> str:
    """Search TMDB for movies by keyword. Returns JSON list of movies."""
    return json.dumps(search_movies_tool(query)[:5], default=str)


@tool
def get_movie_details(movie_id: str) -> str:
    """Get detailed info about a movie by TMDB ID (cast, director, keywords)."""
    return json.dumps(get_movie_details_tool(int(movie_id)), default=str)


@tool
def get_trending_movies(time_window: str = "week") -> str:
    """Get trending movies from TMDB. time_window: 'day' or 'week'."""
    return json.dumps(get_trending_movies_tool(time_window)[:5], default=str)


@tool
def get_similar_movies(movie_id: str) -> str:
    """Get movies similar to a given TMDB movie ID."""
    return json.dumps(get_similar_movies_tool(int(movie_id))[:5], default=str)


@tool
def get_recommendations(user_id: str, query: str = "") -> str:
    """Get personalised movie recommendations for a user based on their DNA profile."""
    return json.dumps(get_recommendations_tool(user_id, query, n=8), default=str)


@tool
def get_user_profile(user_id: str) -> str:
    """Retrieve a user's CineDNA profile including soul profile and character DNA."""
    return json.dumps(get_user_profile_tool(user_id), default=str)


@tool
def get_taste_evolution(user_id: str) -> str:
    """Get the taste evolution history for a user."""
    return json.dumps(get_taste_evolution_tool(user_id), default=str)


AGENT_TOOLS = [
    search_movies,
    get_movie_details,
    get_trending_movies,
    get_similar_movies,
    get_recommendations,
    get_user_profile,
    get_taste_evolution,
]

TOOL_MAP = {t.name: t for t in AGENT_TOOLS}


class CineDNAAgent:
    def __init__(self):
        self._llm = None
        self._llm_with_tools = None

    @property
    def llm(self) -> ChatOllama:
        if self._llm is None:
            self._llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.7,
                num_predict=1024,
            )
        return self._llm

    @property
    def llm_with_tools(self):
        if self._llm_with_tools is None:
            self._llm_with_tools = self.llm.bind_tools(AGENT_TOOLS)
        return self._llm_with_tools

    def _build_system(self, context: str) -> str:
        return f"""You are CineDNA — a deeply knowledgeable movie companion who talks like a passionate film-loving friend. /no_think

PERSONALITY:
- You speak naturally, like someone who genuinely loves cinema and is excited to talk about it.
- You're warm, opinionated, and personal. You say "I think", "honestly", "here's what I love about that".
- You connect movies to emotions, life experiences, and the human condition — not just plot summaries.
- You treat every recommendation like a personal suggestion to a close friend, explaining *why* it fits them.

RESPONSE STYLE:
- Write in flowing, natural paragraphs. Like you're talking to someone over coffee about movies.
- Keep responses focused and concise — 2 to 4 paragraphs max for most answers.
- Use bold sparingly for movie titles or key emphasis only. Example: **Inception**, **The Dark Knight**.
- Use bullet points only when listing 3+ movie titles. Keep bullets short — just the title and a one-line reason.
- Never use markdown headers (no #, ##, ###). Never use tables. Never use horizontal rules.
- Never structure your response like a report or encyclopedia article.
- Don't repeat the user's question back to them.
- When discussing a movie, weave the details naturally into your thoughts. Don't list cast/director/year like a database entry.

BAD example (do NOT do this):
"### Plot Summary
The film follows a group of...
### Cast
- Leonardo DiCaprio as Cobb
### Why It Fits Your DNA
This matches your preference for..."

GOOD example (do this):
"Oh, you'd absolutely love **Inception**. It's Nolan at his most ambitious — the whole thing plays like a puzzle box that keeps folding in on itself. DiCaprio brings this quiet desperation to Cobb that makes the heist stuff feel deeply personal. And honestly, the way it blurs the line between dreams and reality? That's exactly the kind of cerebral thriller that seems to light you up."

{context}"""

    def chat(self, user_id: str, message: str, history: List[Dict]) -> str:
        context = rag_pipeline.build_context(user_id, message)
        messages = [SystemMessage(content=self._build_system(context))]
        for h in history[-6:]:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))
        messages.append(HumanMessage(content=message))

        # Agentic loop: allow up to 3 tool calls
        for _ in range(3):
            response = self.llm_with_tools.invoke(messages)
            if not response.tool_calls:
                break
            messages.append(response)
            for tc in response.tool_calls:
                tool_fn = TOOL_MAP.get(tc["name"])
                if tool_fn:
                    result = tool_fn.invoke(tc["args"])
                    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        final = self.llm.invoke(messages)
        response_text = final.content.strip()

        db.add_chat_message(user_id, "user", message)
        db.add_chat_message(user_id, "assistant", response_text)
        return response_text

    async def stream_chat(self, user_id: str, message: str, history: List[Dict]) -> AsyncIterator[str]:
        context = rag_pipeline.build_context(user_id, message)
        messages = [SystemMessage(content=self._build_system(context))]
        for h in history[-6:]:
            if h["role"] == "user":
                messages.append(HumanMessage(content=h["content"]))
            else:
                messages.append(AIMessage(content=h["content"]))
        messages.append(HumanMessage(content=message))

        # Quick tool resolution (non-streaming) before streaming final response
        for _ in range(2):
            response = self.llm_with_tools.invoke(messages)
            if not response.tool_calls:
                break
            messages.append(response)
            for tc in response.tool_calls:
                tool_fn = TOOL_MAP.get(tc["name"])
                if tool_fn:
                    result = tool_fn.invoke(tc["args"])
                    messages.append(ToolMessage(content=str(result), tool_call_id=tc["id"]))

        # Stream final answer
        stream_llm = ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.7,
            num_predict=1024,
        )
        full_response = ""
        async for chunk in stream_llm.astream(messages):
            token = chunk.content
            if token:
                full_response += token
                yield token

        db.add_chat_message(user_id, "user", message)
        db.add_chat_message(user_id, "assistant", full_response)


agent = CineDNAAgent()
