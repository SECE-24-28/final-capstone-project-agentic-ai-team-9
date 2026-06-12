import re
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import settings


DNA_SYSTEM_PROMPT = """You are CineDNA, an expert movie psychologist. /no_think
Analyze the user's movie preferences and generate a deep psychological profile.
Be insightful, specific, and reveal hidden patterns in plain prose (no markdown, no bullet points, no asterisks).
Keep each response to 2-3 clear, flowing sentences."""


class DNAProfiler:
    def __init__(self):
        self._llm = None

    @property
    def llm(self) -> ChatOllama:
        if self._llm is None:
            self._llm = ChatOllama(
                model=settings.OLLAMA_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.7,
                num_predict=512,
            )
        return self._llm

    def _clean(self, text: str) -> str:
        """Strip markdown bold/italic/heading markers from LLM output."""
        text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)   # **bold** / *italic*
        text = re.sub(r'_{1,2}([^_]+)_{1,2}', r'\1', text)      # __bold__ / _italic_
        text = re.sub(r'#+\s*', '', text)                         # headings
        text = re.sub(r'^[-•]\s+', '', text, flags=re.MULTILINE) # bullet points
        # Remove label prefixes like "SOUL TYPE Profile:" at the start
        text = re.sub(r'^[A-Z ]+PROFILE:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^[A-Z ]+ANALYSIS:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^[A-Z ]+REVEALED:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^VALUES REVEALED:?\s*', '', text, flags=re.IGNORECASE)
        return text.strip()

    def generate_soul_profile(self, movies: list, genres: list) -> str:
        prompt = f"""Favorite movies: {', '.join(movies)}
Favorite genres: {', '.join(genres)}

Write a 2-3 sentence soul type profile for this viewer. Describe their psychological archetype
and the deeper emotional needs their choices reveal. Use plain prose only."""
        response = self.llm.invoke([
            SystemMessage(content=DNA_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return self._clean(response.content)

    def generate_character_dna(self, characters: list, movies: list) -> str:
        if characters:
            char_text = f"Favorite characters: {', '.join(characters)}\nFrom movies: {', '.join(movies)}"
        else:
            char_text = f"Movies watched: {', '.join(movies)} (no specific characters listed)"
        prompt = f"""{char_text}

Write a 2-3 sentence character DNA analysis. What personality traits and values does this viewer
admire in fictional characters? What does this reveal about them? Use plain prose only."""
        response = self.llm.invoke([
            SystemMessage(content=DNA_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return self._clean(response.content)

    def generate_hidden_taste(self, movies: list, genres: list, characters: list) -> str:
        char_context = f"Characters they love: {', '.join(characters)}" if characters else "No specific characters listed"
        prompt = f"""Favorite movies: {', '.join(movies)}
Favorite genres: {', '.join(genres)}
{char_context}

Write 2-3 sentences revealing this viewer's hidden taste. What unexpected genre or theme
would they secretly love? What surprising pattern lies beneath their choices? Use plain prose only."""
        response = self.llm.invoke([
            SystemMessage(content=DNA_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return self._clean(response.content)

    def generate_full_dna(self, data: Dict[str, Any]) -> Dict[str, str]:
        movies = data.get("favorite_movies", [])
        characters = data.get("favorite_characters", [])
        genres = data.get("favorite_genres", [])
        return {
            "soul_profile": self.generate_soul_profile(movies, genres),
            "character_dna": self.generate_character_dna(characters, movies),
            "hidden_taste": self.generate_hidden_taste(movies, genres, characters),
        }

    def analyze_taste_evolution(self, ratings: list, history: list) -> str:
        if not ratings and not history:
            return "Not enough data to analyze taste evolution yet."
        prompt = f"""Recent ratings: {ratings[:5]}
Recommendation history: {[h['movie_title'] for h in history[:10]]}

Write 3-4 sentences analyzing how this viewer's taste has evolved. What new genres or themes
are they gravitating toward? Use plain prose only."""
        response = self.llm.invoke([
            SystemMessage(content=DNA_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return self._clean(response.content)


dna_profiler = DNAProfiler()
