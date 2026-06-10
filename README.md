# CineDNA: Agentic AI Movie Companion 🎬

CineDNA is a highly personalized AI movie recommendation platform. Moving beyond traditional algorithmic suggestions, CineDNA leverages local LLMs (Qwen 3 via LangChain and Ollama) to analyze your "Movie DNA" – your favorite movies, characters, and genres. It constructs a deep psychological profile of your tastes, generates intelligent recommendations, tracks the evolution of your preferences over time, and even autonomously queries TMDB for live movie data.

## Features ✨
- **Movie DNA Profiling:** Discovers your Soul Type, Character DNA, and Hidden Taste based on your core favorites.
- **Agentic Workflow:** The LangChain agent intelligently determines when to use the TMDB API tool to fetch cast, crew, and real-time movie details.
- **Taste Evolution Tracker:** Logs your movie ratings and analyzes how your tastes evolve over time.
- **Fully Local & Private:** Powered by a local Ollama instance (Qwen3) ensuring maximum privacy and zero API costs.
- **Premium UI:** Built on Streamlit with a highly polished, responsive glassmorphism aesthetic.

## Architecture 🏗️
- **Frontend:** Streamlit
- **AI Framework:** LangChain (`langchain-ollama`, `langchain-core`)
- **LLM Engine:** Ollama (Qwen3 1.7b)
- **Database:** SQLite (Custom automated migrations and memory tracking)
- **External APIs:** TMDB API (Integrated via LangChain tools)

## Installation & Usage 🚀

### Prerequisites
1. Python 3.9+
2. [Ollama](https://ollama.ai/) installed on your machine.
3. A TMDB API Key.

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your TMDB API Key:
   ```env
   TMDB_API_KEY=your_api_key_here
   ```
4. Start the Ollama server and ensure the Qwen3 model is available:
   ```bash
   ollama serve
   ollama pull qwen3:1.7b
   ```
5. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

## Contributors 👥
- **Nivash M**
- **Rithish Barath S R**
- **Vishal M K**

---
*Developed for the Final Capstone Project - Agentic AI (Team 9)*
