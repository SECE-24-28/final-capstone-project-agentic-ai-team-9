"""
CineDNA – LangChain + Ollama (Qwen3 1.7b) LLM layer.

Architecture:
  Streamlit → LangChain chains → ChatOllama → SQLite memory
  TMDB Tool called when user asks about specific movies.
"""

import re
import time
import logging
from typing import Iterator

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CineDNA.LLM")

# --------------------------------------------------------------------------- #
#  Model Configuration                                                         #
# --------------------------------------------------------------------------- #
PRIMARY_MODEL  = "qwen3:1.7b"
FALLBACK_MODEL = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest"

MAX_CONTEXT_MESSAGES = 8


def _make_llm(model: str, temperature: float = 0.7, num_predict: int = 512) -> ChatOllama:
    return ChatOllama(
        model=model,
        temperature=temperature,
        num_predict=num_predict,
        num_ctx=4096,
    )


def _get_llm(temperature: float = 0.7, num_predict: int = 512) -> ChatOllama:
    return _make_llm(PRIMARY_MODEL, temperature, num_predict)


def _get_profile_llm() -> ChatOllama:
    return _get_llm(temperature=0.75, num_predict=400)


def _get_chat_llm() -> ChatOllama:
    return _get_llm(temperature=0.7, num_predict=600)


def _strip_think(text: str) -> str:
    """Remove Qwen3 chain-of-thought <think>…</think> blocks from output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


parser = StrOutputParser()


# --------------------------------------------------------------------------- #
#  Prompt Templates                                                            #
# --------------------------------------------------------------------------- #
SYSTEM_PROMPT = """\
You are CineDNA, a deeply personalized AI Movie Companion.

Your role:
• Recommend movies that precisely match the user's Movie DNA profile.
• Explain WHY each recommendation fits their specific taste.
• Discuss their Character DNA, Soul Type, and Hidden Taste on request.
• Be warm, insightful, and concise — no walls of text.

Recommendation format (use this EVERY time):
🎬 **Title** (Year)
Why: [One sentence connecting this film to their specific DNA profile]

Give 3 recommendations by default unless asked for more or fewer.
"""

DNA_PROMPT_TEMPLATE = """\
Analyze this person's movie taste and create a concise Movie DNA Profile.

Favorite Movies: {movies}
Favorite Characters: {characters}
Most Watched Genres: {genres}

Respond in EXACTLY this format — be creative but keep each section to 1-2 sentences:
Soul Type: [A creative label + one sentence describing their cinematic soul]
Character DNA: [What their character choices reveal about their personality]
Hidden Taste Discovery: [One unexpected genre or style they'd love and why]"""

RECOMMENDATION_PROMPT_TEMPLATE = """\
You are CineDNA. Generate personalized movie recommendations.

USER MOVIE DNA:
- Soul Type: {soul_profile}
- Character DNA: {character_dna}
- Hidden Taste: {hidden_taste}
- Favorite Movies: {favorite_movies}
- Favorite Characters: {favorite_characters}
- Favorite Genres: {favorite_genres}

USER QUERY: {query}

For each recommendation, use this format:
🎬 **Title** (Year)
Why: [Specific reason connecting to THEIR DNA — reference their soul type, characters, or genres]

Give exactly 3 recommendations unless asked otherwise. Be specific, not generic."""

EVOLUTION_PROMPT_TEMPLATE = """\
Analyze this user's taste evolution based on their ratings.

Recent Ratings:
{ratings_summary}

Previous Preferences: {previous_prefs}
Current Preferences: {current_prefs}

Write a SHORT insight (2-3 sentences) about how their taste has evolved.
Format:
Previous: [what they used to prefer]
Current: [what they now enjoy]
Insight: [what this evolution reveals about them]"""


# --------------------------------------------------------------------------- #
#  Rule-Based DNA Fallback                                                    #
# --------------------------------------------------------------------------- #
_SOUL_TEMPLATES = {
    "sci-fi":    "The Cosmic Visionary — drawn to stories that question the fabric of reality.",
    "thriller":  "The Edge-of-Seat Strategist — craves tension, twists, and psychological depth.",
    "romance":   "The Hopeful Romantic — believes in the transformative power of human connection.",
    "action":    "The Kinetic Adventurer — lives for momentum, stakes, and triumphant heroes.",
    "drama":     "The Empathic Observer — finds beauty in flawed, authentic human stories.",
    "horror":    "The Thrill Seeker — fascinated by the darkness at the edge of the ordinary.",
    "comedy":    "The Joyful Contrarian — uses humor as a lens to see the world differently.",
    "fantasy":   "The World Builder — longs for myths, magic, and epic journeys of self-discovery.",
    "animation": "The Eternal Optimist — finds profound truths in the art of imagination.",
    "default":   "The Eclectic Cinephile — a rare soul who finds magic across all genres.",
}

_DNA_TEMPLATES = {
    "sci-fi":   "You're drawn to intellectual, innovative characters who challenge the status quo and think in systems.",
    "thriller": "You admire characters who stay calm under pressure, think strategically, and never reveal their full hand.",
    "romance":  "You connect with emotionally intelligent characters who are vulnerable yet resilient in love.",
    "action":   "You root for determined, physically capable heroes who protect what matters most.",
    "drama":    "You're drawn to complex, morally grey characters whose inner struggles mirror real life.",
    "default":  "Your character choices reveal a nuanced personality that values both strength and depth.",
}

_HIDDEN_TASTE = {
    "sci-fi":    "Try **neo-noir** — its moral ambiguity and dystopian atmosphere will resonate with your love of dark futures.",
    "thriller":  "Explore **psychological horror** — it offers the same mind-games you love, with deeper dread.",
    "romance":   "Discover **indie drama** — raw, unpolished love stories with no Hollywood endings.",
    "action":    "Give **war epics** a chance — the same stakes and brotherhood, with historical weight.",
    "drama":     "Try **foreign cinema** — Korean thrillers and French dramas deliver your preferred emotional intensity.",
    "default":   "Explore **A24 films** — their blend of arthouse craft and genre storytelling is tailor-made for eclectic viewers.",
}


def _rule_based_dna(favorite_genres: str, favorite_movies: str) -> dict:
    """Generate a rule-based DNA profile when LLM is unavailable."""
    genres_lower = (favorite_genres or "").lower()
    movies_lower = (favorite_movies or "").lower()

    detected = "default"
    priority = ["sci-fi", "thriller", "romance", "action", "drama", "horror",
                "comedy", "fantasy", "animation"]
    for genre in priority:
        if genre in genres_lower or genre in movies_lower:
            detected = genre
            break

    return {
        "soul_profile":  _SOUL_TEMPLATES.get(detected, _SOUL_TEMPLATES["default"]),
        "character_dna": _DNA_TEMPLATES.get(detected, _DNA_TEMPLATES["default"]),
        "hidden_taste":  _HIDDEN_TASTE.get(detected, _HIDDEN_TASTE["default"]),
    }


# --------------------------------------------------------------------------- #
#  Phase 2: Movie DNA Chain                                                   #
# --------------------------------------------------------------------------- #
def generate_full_profile(favorite_movies: str, favorite_characters: str,
                          favorite_genres: str) -> dict:
    """
    Generate soul_profile, character_dna, hidden_taste from user inputs.
    Uses LLM with /no_think for speed; falls back to rule-based — NEVER returns 'failed'.
    """
    start = time.time()
    logger.info("Generating Movie DNA for: movies=%s chars=%s genres=%s",
                favorite_movies[:40], favorite_characters[:40], favorite_genres[:40])

    prompt = ChatPromptTemplate.from_messages([
        ("human", DNA_PROMPT_TEMPLATE)
    ])
    chain = prompt | _get_profile_llm() | parser

    content = ""
    try:
        content = chain.invoke({
            "movies":     favorite_movies or "Not specified",
            "characters": favorite_characters or "Not specified",
            "genres":     favorite_genres or "Not specified",
        })
        content = _strip_think(content)
        logger.info("Raw DNA response (%d chars): %s", len(content), content[:200])
    except Exception as e:
        logger.error("LLM DNA generation failed: %s", e)

    # Parse structured sections
    soul    = _parse_section(content, "Soul Type")
    dna     = _parse_section(content, "Character DNA")
    hidden  = _parse_section(content, "Hidden Taste Discovery") or _parse_section(content, "Hidden Taste")

    # If any field is missing, blend partial LLM output with rule-based fallback
    if not soul or not dna or not hidden:
        logger.warning("Partial parse — supplementing with rule-based fallback.")
        fallback = _rule_based_dna(favorite_genres, favorite_movies)
        soul   = soul   or fallback["soul_profile"]
        dna    = dna    or fallback["character_dna"]
        hidden = hidden or fallback["hidden_taste"]

    elapsed = time.time() - start
    logger.info("DNA generated in %.2fs: soul=%s", elapsed, soul[:50])

    return {
        "soul_profile":  soul,
        "character_dna": dna,
        "hidden_taste":  hidden,
        "llm_time":      elapsed,
    }


# --------------------------------------------------------------------------- #
#  Phase 3: Personalized Recommendation Chain                                 #
# --------------------------------------------------------------------------- #
def get_personalized_recommendations(user_query: str, user_profile: dict) -> str:
    """
    Generate richly personalized recommendations tied to the user's Movie DNA.
    Falls back to general chat chain if profile is empty.
    """
    if not user_profile.get("soul_profile"):
        return None

    start = time.time()
    prompt = ChatPromptTemplate.from_messages([
        ("human", RECOMMENDATION_PROMPT_TEMPLATE)
    ])
    chain = prompt | _get_chat_llm() | parser

    try:
        content = chain.invoke({
            "soul_profile":        user_profile.get("soul_profile", ""),
            "character_dna":       user_profile.get("character_dna", ""),
            "hidden_taste":        user_profile.get("hidden_taste", ""),
            "favorite_movies":     user_profile.get("favorite_movies", ""),
            "favorite_characters": user_profile.get("favorite_characters", ""),
            "favorite_genres":     user_profile.get("favorite_genres", ""),
            "query":               user_query,
        })
        content = _strip_think(content)
        logger.info("Personalized recs generated in %.2fs", time.time() - start)
        return content
    except Exception as e:
        logger.error("Personalized recommendation chain failed: %s", e)
        return None


# --------------------------------------------------------------------------- #
#  Phase 5: Conversation Memory helpers                                       #
# --------------------------------------------------------------------------- #
def _build_context_summary(user_profile: dict) -> str:
    """Compress profile into a compact LLM context string."""
    parts = []
    if user_profile.get("soul_profile"):
        parts.append(f"Soul: {user_profile['soul_profile'][:80]}")
    if user_profile.get("character_dna"):
        parts.append(f"DNA: {user_profile['character_dna'][:80]}")
    if user_profile.get("hidden_taste"):
        parts.append(f"Hidden: {user_profile['hidden_taste'][:60]}")
    if user_profile.get("favorite_genres"):
        parts.append(f"Genres: {user_profile['favorite_genres']}")
    if user_profile.get("favorite_movies"):
        parts.append(f"Movies: {user_profile['favorite_movies']}")
    if user_profile.get("favorite_characters"):
        parts.append(f"Characters: {user_profile['favorite_characters']}")
    if user_profile.get("taste_evolution"):
        parts.append(f"Evolution: {user_profile['taste_evolution'][:80]}")
    return " | ".join(parts)


def _build_messages(user_input: str, chat_history: list, user_profile: dict) -> list:
    """Build LangChain message list with system prompt + profile + history."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    context = _build_context_summary(user_profile)
    if context:
        messages.append(SystemMessage(content=f"USER MOVIE DNA:\n{context}"))

    # Trim and inject history
    if chat_history:
        history = chat_history[-(MAX_CONTEXT_MESSAGES):]
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=user_input))
    return messages


# --------------------------------------------------------------------------- #
#  Phase 7: Main Chat Response (streaming)                                    #
# --------------------------------------------------------------------------- #
def get_movie_chat_response(user_input: str, chat_history: list = None,
                             user_profile: dict = None,
                             stream: bool = True) -> Iterator[str]:
    """
    Main entry point for streaming chat responses.

    Flow:
    1. Recommendation request + DNA profile → personalized recommendation chain.
    2. Otherwise → standard conversational chain with full profile context.

    Think-tag stripping: Qwen3 may emit <think>…</think> blocks. Because the
    tags are split across many stream chunks, we CANNOT filter chunk-by-chunk.
    Instead we buffer the full response, strip think blocks, then yield clean
    text token by token so the UI still shows a live stream effect.
    """
    chat_history = chat_history or []
    user_profile  = user_profile or {}
    start = time.time()
    llm   = _get_chat_llm()

    rec_keywords = {"recommend", "suggest", "what should", "what to watch",
                    "similar to", "movies for me", "top ", "best "}
    is_rec_request = any(kw in user_input.lower() for kw in rec_keywords)

    def _stream_buffered(chain_obj, invoke_input):
        """Buffer full response, strip think tags, yield word by word."""
        raw = ""
        try:
            for chunk in chain_obj.stream(invoke_input):
                raw += chunk
        except Exception as e:
            logger.error("Stream error: %s", e)
            yield "I'm having trouble connecting right now. Please try again."
            return
        clean = _strip_think(raw)
        elapsed = time.time() - start
        logger.info("Stream done: %.2fs | raw=%d clean=%d chars",
                    elapsed, len(raw), len(clean))
        # Yield word-by-word for live feel
        words = clean.split(" ")
        for i, word in enumerate(words):
            yield word + (" " if i < len(words) - 1 else "")

    if is_rec_request and user_profile.get("soul_profile"):
        logger.info("Using personalized recommendation chain.")
        prompt = ChatPromptTemplate.from_messages(
            [("human", RECOMMENDATION_PROMPT_TEMPLATE)]
        )
        chain = prompt | llm | parser
        try:
            yield from _stream_buffered(chain, {
                "soul_profile":        user_profile.get("soul_profile", ""),
                "character_dna":       user_profile.get("character_dna", ""),
                "hidden_taste":        user_profile.get("hidden_taste", ""),
                "favorite_movies":     user_profile.get("favorite_movies", ""),
                "favorite_characters": user_profile.get("favorite_characters", ""),
                "favorite_genres":     user_profile.get("favorite_genres", ""),
                "query":               user_input,
            })
            return
        except Exception as e:
            logger.error("Rec chain failed, falling back: %s", e)

    # Standard conversational chain
    messages = _build_messages(user_input, chat_history, user_profile)
    yield from _stream_buffered(llm | parser, messages)


# --------------------------------------------------------------------------- #
#  Phase 8: Taste Evolution                                                   #
# --------------------------------------------------------------------------- #
def generate_taste_evolution(ratings: list, previous_prefs: str,
                              current_prefs: str) -> str:
    """Generate an evolving taste insight from rating history."""
    if not ratings:
        return ""

    ratings_summary = "\n".join(
        f"• {r['movie_name']}: {r['rating']}/10" for r in ratings[:10]
    )

    prompt = ChatPromptTemplate.from_messages(
        [("human", EVOLUTION_PROMPT_TEMPLATE)]
    )
    chain  = prompt | _get_profile_llm() | parser

    try:
        content = chain.invoke({
            "ratings_summary": ratings_summary,
            "previous_prefs":  previous_prefs or "Unknown",
            "current_prefs":   current_prefs or "Unknown",
        })
        return _strip_think(content)
    except Exception as e:
        logger.error("Taste evolution generation failed: %s", e)
        return ""


# --------------------------------------------------------------------------- #
#  Section parser                                                              #
# --------------------------------------------------------------------------- #
def _parse_section(content: str, keyword: str) -> str:
    if not content:
        return ""
    pattern = re.compile(
        re.escape(keyword) + r"[*:\s]*(.*?)(?=\n\s*(?:Soul Type|Character DNA|Hidden Taste)|$)",
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.search(content)
    if match:
        text = match.group(1).strip().replace("**", "").replace("*", "")
        if len(text) > 5:
            return text
    return ""
