"""Quick test: LangChain + Google Gemini."""
from llm import get_movie_chat_response, generate_full_profile
import time

# Test 1: Chat streaming
print("=== Chat Streaming ===")
start = time.time()
gen = get_movie_chat_response("recommend 3 sci-fi movies", stream=True)
full = ""
for chunk in gen:
    full += chunk
print(f"Time: {time.time() - start:.1f}s | Chars: {len(full)}")
print(full[:400])

# Test 2: Profile generation
print("\n=== Profile Generation ===")
start = time.time()
result = generate_full_profile("Inception, The Matrix, Interstellar", "Dom Cobb, Neo, Cooper", "Sci-Fi, Thriller")
print(f"Time: {time.time() - start:.1f}s")
print(f"Soul: {result['soul_profile']}")
print(f"DNA:  {result['character_dna']}")
print(f"Taste: {result['hidden_taste']}")
