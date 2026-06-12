import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { generateDNA } from '../api/client'
import './MovieDNA.css'

const GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi', 'Thriller',
  'Romance', 'Animation', 'Documentary', 'Fantasy', 'Mystery', 'Crime']

export default function MovieDNA({ userId }) {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const [movies, setMovies] = useState([])
  const [movieInput, setMovieInput] = useState('')
  const [characters, setCharacters] = useState([])
  const [charInput, setCharInput] = useState('')
  const [genres, setGenres] = useState([])

  const addTag = (list, setList, input, setInput) => {
    const val = input.trim()
    if (val && !list.includes(val)) setList([...list, val])
    setInput('')
  }
  const removeTag = (list, setList, val) => setList(list.filter((x) => x !== val))
  const toggleGenre = (g) => setGenres((prev) => prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g])

  const handleSubmit = async () => {
    if (!movies.length || !genres.length) { setError('Add at least 1 movie and 1 genre.'); return }
    setLoading(true); setError('')
    try {
      const res = await generateDNA({ user_id: userId, favorite_movies: movies, favorite_characters: characters, favorite_genres: genres })
      setResult(res.data.dna)
      setStep(3)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to generate DNA. Is the backend running?')
    } finally { setLoading(false) }
  }

  if (result) return (
    <div className="page dna-page fade-up">
      <div className="dna-result">
        <h1>Your <span className="grad-text">Movie DNA</span> 🧬</h1>
        <p className="page-header-sub">Your psychological cinematic profile has been decoded.</p>
        <div className="dna-cards">

          {/* Soul Type */}
          <div className="dna-card glass-card">
            <div className="dna-card-header">
              <span className="dna-card-icon">🔮</span>
              <div>
                <div className="dna-card-label">Soul Type</div>
                <div className="dna-card-badge">Psychological Archetype</div>
              </div>
            </div>
            <div className="dna-card-divider" />
            <p className="dna-card-body">{result.soul_profile || 'Generating your soul type…'}</p>
          </div>

          {/* Character DNA */}
          <div className="dna-card glass-card">
            <div className="dna-card-header">
              <span className="dna-card-icon">🎭</span>
              <div>
                <div className="dna-card-label">Character DNA</div>
                <div className="dna-card-badge">Values & Traits</div>
              </div>
            </div>
            <div className="dna-card-divider" />
            <p className="dna-card-body">{result.character_dna || 'Generating character DNA…'}</p>
          </div>

          {/* Hidden Taste */}
          <div className="dna-card glass-card dna-card--accent">
            <div className="dna-card-header">
              <span className="dna-card-icon">🕵️</span>
              <div>
                <div className="dna-card-label">Hidden Taste</div>
                <div className="dna-card-badge">Secret Pattern</div>
              </div>
            </div>
            <div className="dna-card-divider" />
            <p className="dna-card-body">{result.hidden_taste || 'Uncovering hidden patterns…'}</p>
          </div>

        </div>

        {/* Input summary */}
        <div className="dna-inputs-summary glass-card">
          <div className="dna-input-group">
            <span className="dna-input-label">🎬 Movies</span>
            <div className="tags-row">{movies.map(m => <span key={m} className="tag tag--readonly">{m}</span>)}</div>
          </div>
          <div className="dna-input-group">
            <span className="dna-input-label">🎪 Genres</span>
            <div className="tags-row">{genres.map(g => <span key={g} className="tag tag--genre">{g}</span>)}</div>
          </div>
          {characters.length > 0 && (
            <div className="dna-input-group">
              <span className="dna-input-label">🎭 Characters</span>
              <div className="tags-row">{characters.map(c => <span key={c} className="tag tag--readonly">{c}</span>)}</div>
            </div>
          )}
        </div>

        <div className="dna-actions">
          <button className="btn btn-primary" onClick={() => navigate('/recommendations')}>🎬 See Recommendations</button>
          <button className="btn btn-ghost" onClick={() => navigate('/chat')}>💬 Chat with AI</button>
        </div>
      </div>
    </div>
  )


  return (
    <div className="page dna-page fade-up">
      <div className="page-header">
        <h1>Decode Your <span className="grad-text">Movie DNA</span></h1>
        <p>Answer 3 questions. We'll build your cinematic soul profile.</p>
      </div>
      <div className="dna-stepper">
        {['Movies', 'Characters', 'Genres'].map((s, i) => (
          <div key={i} className={`step ${step >= i ? 'active' : ''} ${step > i ? 'done' : ''}`}>
            <div className="step-dot">{step > i ? '✓' : i + 1}</div>
            <span>{s}</span>
          </div>
        ))}
      </div>

      <div className="dna-form glass-card">
        {step === 0 && (
          <div className="form-step">
            <h2>🎬 Favorite Movies</h2>
            <p>Name the movies that shaped you. At least 1.</p>
            <div className="tag-input-row">
              <input className="input" value={movieInput} onChange={e => setMovieInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addTag(movies, setMovies, movieInput, setMovieInput)}
                placeholder="e.g. Inception, Interstellar" />
              <button className="btn btn-primary" onClick={() => addTag(movies, setMovies, movieInput, setMovieInput)}>Add</button>
            </div>
            <div className="tags-row">{movies.map(m => <span key={m} className="tag">{m}<button onClick={() => removeTag(movies, setMovies, m)}>×</button></span>)}</div>
            <button className="btn btn-primary step-next" onClick={() => setStep(1)} disabled={!movies.length}>Next →</button>
          </div>
        )}
        {step === 1 && (
          <div className="form-step">
            <h2>🎭 Favorite Characters</h2>
            <p>Which fictional characters resonate with you? (optional)</p>
            <div className="tag-input-row">
              <input className="input" value={charInput} onChange={e => setCharInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addTag(characters, setCharacters, charInput, setCharInput)}
                placeholder="e.g. Tony Stark, Hermione" />
              <button className="btn btn-primary" onClick={() => addTag(characters, setCharacters, charInput, setCharInput)}>Add</button>
            </div>
            <div className="tags-row">{characters.map(c => <span key={c} className="tag">{c}<button onClick={() => removeTag(characters, setCharacters, c)}>×</button></span>)}</div>
            <div className="step-nav">
              <button className="btn btn-ghost" onClick={() => setStep(0)}>← Back</button>
              <button className="btn btn-primary" onClick={() => setStep(2)}>Next →</button>
            </div>
          </div>
        )}
        {step === 2 && (
          <div className="form-step">
            <h2>🎪 Favorite Genres</h2>
            <p>Pick your go-to genres. At least 1.</p>
            <div className="genre-grid">
              {GENRES.map(g => (
                <button key={g} className={`genre-btn ${genres.includes(g) ? 'selected' : ''}`} onClick={() => toggleGenre(g)}>{g}</button>
              ))}
            </div>
            {error && <div className="alert alert-error">{error}</div>}
            <div className="step-nav">
              <button className="btn btn-ghost" onClick={() => setStep(1)}>← Back</button>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={loading || !genres.length}>
                {loading ? '🧬 Analysing...' : '🚀 Generate My DNA'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
