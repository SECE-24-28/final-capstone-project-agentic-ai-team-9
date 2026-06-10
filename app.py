"""
CineDNA – Streamlit app.
Personalized AI Movie Companion powered by LangChain + Ollama (Qwen3).
"""

import streamlit as st
import time

from llm import (
    get_movie_chat_response,
    generate_full_profile,
    generate_taste_evolution,
    MAX_CONTEXT_MESSAGES,
)
from database import (
    save_message, get_recent_messages,
    get_user_profile, save_user_preferences,
    clear_user_profile,
    save_movie_rating, get_user_ratings,
)
from tmdb import search_movie, get_movie_details, tmdb_details_tool

# --------------------------------------------------------------------------- #
#  Page config                                                                 #
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="CineDNA – Your Movie Companion",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
#  Custom CSS – premium dark glassmorphism                                    #
# --------------------------------------------------------------------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0f0c29 40%, #1a1a2e 75%, #16213e 100%);
    min-height: 100vh;
}

/* Header */
.cine-header {
    background: linear-gradient(90deg, #e94560, #ff6b6b, #feca57);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 4px;
}
.cine-sub {
    color: #7b7f94;
    font-size: 0.95rem;
    font-weight: 400;
    margin-top: 0;
    letter-spacing: 0.5px;
}

/* Profile cards */
.dna-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 12px;
    border-left: 4px solid #e94560;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, border-color 0.2s ease;
}
.dna-card:hover {
    transform: translateX(3px);
    border-left-color: #feca57;
}
.dna-label {
    color: #e94560;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.dna-value {
    color: #e8e9f0;
    font-size: 0.92rem;
    line-height: 1.5;
}

/* Onboarding */
.onboard-step {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(233,69,96,0.2);
    border-radius: 16px;
    padding: 28px 32px;
    margin: 20px 0;
}
.step-badge {
    display: inline-block;
    background: linear-gradient(135deg, #e94560, #ff6b6b);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
    margin-bottom: 10px;
}

/* Chat messages */
.stChatMessage {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
}

/* Sidebar */
.sidebar-section {
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.07);
}
.sidebar-title {
    color: #e94560;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Progress steps */
.step-progress {
    display: flex;
    gap: 8px;
    margin-bottom: 20px;
}
.step-dot {
    width: 28px;
    height: 6px;
    border-radius: 3px;
    background: rgba(255,255,255,0.1);
    transition: background 0.3s;
}
.step-dot.active {
    background: linear-gradient(90deg, #e94560, #ff6b6b);
}
.step-dot.done {
    background: #27ae60;
}

/* Rating stars */
.rating-display {
    color: #feca57;
    font-size: 1.1rem;
}

/* Evolution insight */
.evolution-card {
    background: linear-gradient(135deg, rgba(233,69,96,0.08), rgba(254,202,87,0.08));
    border: 1px solid rgba(233,69,96,0.25);
    border-radius: 14px;
    padding: 16px 20px;
    margin: 10px 0;
}

/* Perf badge */
.perf-badge {
    background: rgba(39,174,96,0.15);
    color: #27ae60;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.5px;
}

/* Input fields */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e8e9f0 !important;
    border-radius: 10px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #e94560 !important;
    box-shadow: 0 0 0 2px rgba(233,69,96,0.15) !important;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Session state initialisation                                                #
# --------------------------------------------------------------------------- #
if "user_id" not in st.session_state:
    st.session_state.user_id = "guest_user"

if "perf_metrics" not in st.session_state:
    st.session_state.perf_metrics = {}

if "show_rating_input" not in st.session_state:
    st.session_state.show_rating_input = False

# Load profile from DB
profile = get_user_profile(st.session_state.user_id)

if "onboarding_step" not in st.session_state:
    if profile.get("soul_profile"):
        st.session_state.onboarding_step = 5
        st.session_state.messages = get_recent_messages(
            st.session_state.user_id, limit=20
        )
    else:
        st.session_state.onboarding_step = 1
        st.session_state.messages = []


# --------------------------------------------------------------------------- #
#  Header                                                                      #
# --------------------------------------------------------------------------- #
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="cine-header">🎬 CineDNA</p>', unsafe_allow_html=True)
    st.markdown('<p class="cine-sub">Your AI Movie Companion · Powered by Qwen3 + LangChain</p>',
                unsafe_allow_html=True)
with col_h2:
    if st.session_state.perf_metrics.get("llm_time"):
        t = st.session_state.perf_metrics["llm_time"]
        st.markdown(f'<br><span class="perf-badge">⚡ {t:.1f}s</span>',
                    unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Sidebar                                                                     #
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown("### 🧬 CineDNA")

    if st.session_state.onboarding_step == 5 and profile:
        # DNA Summary
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">🧬 Soul Type</p>', unsafe_allow_html=True)
        st.markdown(f"<small style='color:#e8e9f0'>{profile.get('soul_profile','')}</small>",
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">🎭 Character DNA</p>', unsafe_allow_html=True)
        st.markdown(f"<small style='color:#e8e9f0'>{profile.get('character_dna','')}</small>",
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">🔮 Hidden Taste</p>', unsafe_allow_html=True)
        st.markdown(f"<small style='color:#e8e9f0'>{profile.get('hidden_taste','')}</small>",
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Taste evolution (Phase 8)
        if profile.get("taste_evolution"):
            st.markdown('<div class="sidebar-section evolution-card">', unsafe_allow_html=True)
            st.markdown('<p class="sidebar-title">📈 Taste Evolution</p>', unsafe_allow_html=True)
            st.markdown(f"<small style='color:#e8e9f0'>{profile['taste_evolution']}</small>",
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Favorites
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-title">🎬 Your Picks</p>', unsafe_allow_html=True)
        st.markdown(f"<small style='color:#8b8fa3'>Movies: {profile.get('favorite_movies','')}</small>",
                    unsafe_allow_html=True)
        st.markdown(f"<small style='color:#8b8fa3'>Characters: {profile.get('favorite_characters','')}</small>",
                    unsafe_allow_html=True)
        st.markdown(f"<small style='color:#8b8fa3'>Genres: {profile.get('favorite_genres','')}</small>",
                    unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.divider()

        # Phase 4: Movie rating input
        st.markdown("### ⭐ Rate a Movie")
        rating_movie = st.text_input("Movie name", key="rating_movie_input",
                                     placeholder="e.g. Inception")
        rating_val = st.slider("Rating", 0.0, 10.0, 7.0, 0.5, key="rating_slider")
        if st.button("Save Rating", use_container_width=True, key="save_rating_btn"):
            if rating_movie:
                save_movie_rating(st.session_state.user_id, rating_movie, rating_val)
                st.success(f"Rated '{rating_movie}': {rating_val}/10")

                # Phase 8: Update taste evolution after new rating
                ratings = get_user_ratings(st.session_state.user_id, limit=10)
                if len(ratings) >= 3:
                    evolution = generate_taste_evolution(
                        ratings,
                        previous_prefs=profile.get("favorite_genres", ""),
                        current_prefs=", ".join(r["movie_name"] for r in ratings[:5])
                    )
                    if evolution:
                        save_user_preferences(st.session_state.user_id,
                                              taste_evolution=evolution)
                        st.info("Taste evolution updated!")

        # Recent ratings
        ratings = get_user_ratings(st.session_state.user_id, limit=5)
        if ratings:
            st.markdown("**Recent ratings:**")
            for r in ratings:
                stars = "⭐" * int(r["rating"] / 2)
                st.markdown(f"<small style='color:#feca57'>{stars}</small> "
                            f"<small style='color:#e8e9f0'>{r['movie_name']} ({r['rating']}/10)</small>",
                            unsafe_allow_html=True)

        st.divider()

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Retake DNA", use_container_width=True):
                clear_user_profile(st.session_state.user_id)
                st.session_state.onboarding_step = 1
                st.session_state.messages = []
                st.rerun()
        with col_r2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    else:
        st.markdown("""
        <div style='color:#7b7f94; font-size:0.85rem; line-height:1.8'>
        Complete the 3-step DNA analysis to unlock:<br>
        🎬 Personalized recommendations<br>
        🧬 Movie Soul Profile<br>
        🎭 Character DNA analysis<br>
        🔮 Hidden taste discovery<br>
        ⭐ Movie ratings & evolution
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    # Model info
    st.markdown(f"<small style='color:#4a4d5e'>Model: Qwen3 1.7b (Ollama)<br>LangChain powered</small>",
                unsafe_allow_html=True)


# --------------------------------------------------------------------------- #
#  Onboarding Flow (Steps 1–4)                                                #
# --------------------------------------------------------------------------- #
def _step_progress(current: int):
    dots = []
    for i in range(1, 4):
        if i < current:
            cls = "done"
        elif i == current:
            cls = "active"
        else:
            cls = ""
        dots.append(f'<div class="step-dot {cls}"></div>')
    st.markdown(f'<div class="step-progress">{"".join(dots)}</div>', unsafe_allow_html=True)


if st.session_state.onboarding_step < 5:
    st.markdown("---")
    st.markdown("### 🧬 Discover Your Movie DNA")
    st.markdown(
        "<p style='color:#7b7f94; font-size:0.9rem'>"
        "Answer 3 quick questions so your AI companion can understand your taste.</p>",
        unsafe_allow_html=True
    )

    # Step 1: Favorite movies
    if st.session_state.onboarding_step == 1:
        _step_progress(1)
        st.markdown('<div class="onboard-step">', unsafe_allow_html=True)
        st.markdown('<span class="step-badge">STEP 1 OF 3</span>', unsafe_allow_html=True)
        st.markdown("#### 🎬 What are your 3 favorite movies?")
        st.markdown("<small style='color:#7b7f94'>These form the core of your Movie DNA</small>",
                    unsafe_allow_html=True)
        fav_movies = st.text_input(
            "Favorite movies",
            placeholder="e.g. Interstellar, The Matrix, Inception",
            label_visibility="collapsed",
            key="step1_input"
        )
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Next ➡️", use_container_width=True, key="step1_btn"):
                if fav_movies.strip():
                    save_user_preferences(
                        st.session_state.user_id,
                        favorite_movies=fav_movies.strip()
                    )
                    st.session_state.onboarding_step = 2
                    st.rerun()
                else:
                    st.warning("Please enter at least one movie.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 2: Favorite characters
    elif st.session_state.onboarding_step == 2:
        _step_progress(2)
        st.markdown('<div class="onboard-step">', unsafe_allow_html=True)
        st.markdown('<span class="step-badge">STEP 2 OF 3</span>', unsafe_allow_html=True)
        st.markdown("#### 🎭 Who are your favorite movie characters?")
        st.markdown("<small style='color:#7b7f94'>Your character choices reveal your personality DNA</small>",
                    unsafe_allow_html=True)
        fav_chars = st.text_input(
            "Favorite characters",
            placeholder="e.g. Tony Stark, Ellen Ripley, Hermione Granger",
            label_visibility="collapsed",
            key="step2_input"
        )
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Next ➡️", use_container_width=True, key="step2_btn"):
                if fav_chars.strip():
                    save_user_preferences(
                        st.session_state.user_id,
                        favorite_characters=fav_chars.strip()
                    )
                    st.session_state.onboarding_step = 3
                    st.rerun()
                else:
                    st.warning("Please enter at least one character.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 3: Favorite genres
    elif st.session_state.onboarding_step == 3:
        _step_progress(3)
        st.markdown('<div class="onboard-step">', unsafe_allow_html=True)
        st.markdown('<span class="step-badge">STEP 3 OF 3</span>', unsafe_allow_html=True)
        st.markdown("#### 🎞️ Which genres do you watch most?")
        st.markdown("<small style='color:#7b7f94'>This unlocks your hidden taste discoveries</small>",
                    unsafe_allow_html=True)
        fav_genres = st.text_input(
            "Favorite genres",
            placeholder="e.g. Sci-Fi, Thriller, Romantic Comedy",
            label_visibility="collapsed",
            key="step3_input"
        )
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Analyze My DNA 🧬", use_container_width=True, key="step3_btn"):
                if fav_genres.strip():
                    save_user_preferences(
                        st.session_state.user_id,
                        favorite_genres=fav_genres.strip()
                    )
                    st.session_state.onboarding_step = 4
                    st.rerun()
                else:
                    st.warning("Please enter at least one genre.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Step 4: Generating DNA
    elif st.session_state.onboarding_step == 4:
        st.markdown('<div class="onboard-step">', unsafe_allow_html=True)
        st.markdown("#### ⚙️ Analyzing your Movie DNA...")
        progress_bar = st.progress(0, text="Loading your preferences...")

        temp_profile = get_user_profile(st.session_state.user_id)
        progress_bar.progress(20, text="Connecting to AI model...")

        results = generate_full_profile(
            temp_profile.get("favorite_movies", ""),
            temp_profile.get("favorite_characters", ""),
            temp_profile.get("favorite_genres", ""),
        )
        progress_bar.progress(80, text="Saving your DNA...")

        save_user_preferences(
            st.session_state.user_id,
            soul_profile=results["soul_profile"],
            character_dna=results["character_dna"],
            hidden_taste=results["hidden_taste"],
        )
        progress_bar.progress(100, text="Done!")

        st.session_state.perf_metrics = {"llm_time": results["llm_time"]}
        st.session_state.onboarding_step = 5

        welcome_msg = (
            "🎬 Your Movie DNA has been analyzed! Here's what I discovered:\n\n"
            f"🧬 **Soul Type:** {results['soul_profile']}\n\n"
            f"🎭 **Character DNA:** {results['character_dna']}\n\n"
            f"🔮 **Hidden Taste:** {results['hidden_taste']}\n\n"
            "Ask me for personalized recommendations, discuss your profile, "
            "or search for any movie!"
        )
        st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
        save_message(st.session_state.user_id, "assistant", welcome_msg)
        st.markdown('</div>', unsafe_allow_html=True)
        st.rerun()


# --------------------------------------------------------------------------- #
#  Main Chat (Step 5)                                                         #
# --------------------------------------------------------------------------- #
else:
    # DNA Profile Summary (shown once after onboarding)
    if len(st.session_state.messages) <= 1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="dna-card">
                <div class="dna-label">🧬 Soul Type</div>
                <div class="dna-value">{profile.get('soul_profile','')}</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="dna-card">
                <div class="dna-label">🎭 Character DNA</div>
                <div class="dna-value">{profile.get('character_dna','')}</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="dna-card">
                <div class="dna-label">🔮 Hidden Taste</div>
                <div class="dna-value">{profile.get('hidden_taste','')}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("---")

    # Quick action pills
    st.markdown(
        "<p style='color:#7b7f94;font-size:0.8rem;margin-bottom:8px'>Quick actions:</p>",
        unsafe_allow_html=True
    )
    qa_cols = st.columns(4)
    quick_actions = [
        ("🎬 Recommend me 3 movies", "Recommend me 3 movies based on my DNA"),
        ("🔮 Explore my hidden taste", "What are some hidden taste movies I'd enjoy?"),
        ("🎭 Explain my Character DNA", "Explain my Character DNA in detail"),
        ("🌟 What's trending?", "What are some trending movies I'd like?"),
    ]
    for i, (label, query) in enumerate(quick_actions):
        with qa_cols[i]:
            if st.button(label, use_container_width=True, key=f"qa_{i}"):
                st.session_state._quick_query = query

    # Process quick action and chat input
    chat_prompt = st.chat_input("Ask for recommendations, search a movie, or discuss your DNA...")
    
    prompt = None
    if hasattr(st.session_state, "_quick_query"):
        prompt = st.session_state._quick_query
        del st.session_state._quick_query
    elif chat_prompt:
        prompt = chat_prompt

    st.markdown("")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process new prompt
    if prompt:
        total_start = time.time()

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.user_id, "user", prompt)

        # Phase 6: Detect TMDB lookup intent
        tmdb_keywords = {"cast of", "who stars", "who directed", "details about",
                         "tell me about", "info on", "information about", "poster"}
        is_tmdb_query = any(kw in prompt.lower() for kw in tmdb_keywords)

        with st.chat_message("assistant"):
            # TMDB info prefix
            tmdb_context = ""
            if is_tmdb_query:
                # Extract movie name (simple heuristic: words after keyword)
                for kw in sorted(tmdb_keywords, key=len, reverse=True):
                    if kw in prompt.lower():
                        idx = prompt.lower().find(kw) + len(kw)
                        movie_query = prompt[idx:].strip().strip("?").strip()
                        if movie_query:
                            with st.spinner(f"Fetching TMDB data for '{movie_query}'..."):
                                tmdb_info = tmdb_details_tool(movie_query)
                            if tmdb_info and "Could not" not in tmdb_info:
                                tmdb_context = f"\n\n📽️ **TMDB Data:**\n{tmdb_info}\n\n"
                                st.markdown(tmdb_context)
                        break

            # Stream LLM response
            response_placeholder = st.empty()
            full_response = []

            try:
                recent_history = st.session_state.messages[-(MAX_CONTEXT_MESSAGES + 1):-1]

                stream = get_movie_chat_response(
                    prompt,
                    chat_history=recent_history,
                    user_profile=profile,
                    stream=True,
                )

                for token in stream:
                    full_response.append(token)
                    response_placeholder.markdown("".join(full_response) + "▌")

                final_response = "".join(full_response)
                response_placeholder.markdown(final_response)

                total_time = time.time() - total_start
                st.session_state.perf_metrics = {"llm_time": total_time}
                st.caption(f"⚡ {total_time:.1f}s · Qwen3 via Ollama")

                full_to_save = tmdb_context + final_response
                st.session_state.messages.append({"role": "assistant", "content": full_to_save})
                save_message(st.session_state.user_id, "assistant", full_to_save)

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure Ollama is running: `ollama serve`")
