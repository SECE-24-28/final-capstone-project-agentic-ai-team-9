import { useState, useEffect, useRef, useCallback } from 'react'
import {
  getRecommendations,
  generateRecommendations,
  getTrending,
  searchMovies,
} from '../api/client'
import MovieCard from '../components/MovieCard'
import MovieDetailModal from '../components/MovieDetailModal'
import './Recommendations.css'

const MODES = [
  { id: 'dna',     label: '🧬 DNA Picks',  desc: 'Personalised via your Movie DNA' },
  { id: 'search',  label: '🔍 Search',      desc: 'Find any movie by name' },
  { id: 'trending',label: '🔥 Trending',    desc: 'What the world is watching' },
]

export default function Recommendations({ userId }) {
  const [mode, setMode]           = useState('dna')
  const [dnaMovies, setDnaMovies] = useState([])
  const [trendMovies, setTrendMovies] = useState([])
  const [searchResults, setSearchResults] = useState([])
  const [query, setQuery]         = useState('')
  const [dnaQuery, setDnaQuery]   = useState('')
  const [selectedMovie, setSelectedMovie] = useState(null)

  const [loadingDna, setLoadingDna]       = useState(false)
  const [generatingDna, setGeneratingDna] = useState(false)
  const [loadingTrend, setLoadingTrend]   = useState(false)
  const [searching, setSearching]         = useState(false)
  const [error, setError]                 = useState('')

  const debounceRef = useRef(null)

  // ── Load DNA picks on mount ──────────────────────────────────────────────
  const loadDna = useCallback(async () => {
    setLoadingDna(true); setError('')
    try {
      const res = await getRecommendations(userId)
      const data = res.data.recommendations || []
      setDnaMovies(Array.isArray(data) ? data : [])
    } catch {
      setError('Could not load recommendations.')
    } finally { setLoadingDna(false) }
  }, [userId])

  // ── Generate DNA picks ────────────────────────────────────────────────────
  const generateDna = async (customQuery = dnaQuery) => {
    setGeneratingDna(true); setError('')
    try {
      const res = await generateRecommendations({ user_id: userId, query: customQuery, n: 12 })
      const data = res.data.recommendations || []
      setDnaMovies(Array.isArray(data) ? data : [])
    } catch {
      setError('Failed to generate. Make sure your Movie DNA is set up first.')
    } finally { setGeneratingDna(false) }
  }

  // ── Load trending ─────────────────────────────────────────────────────────
  const loadTrending = useCallback(async () => {
    if (trendMovies.length) return          // already fetched
    setLoadingTrend(true)
    try {
      const res = await getTrending()
      setTrendMovies(res.data.trending || [])
    } catch {
      setError('Could not load trending movies.')
    } finally { setLoadingTrend(false) }
  }, [trendMovies.length])

  // ── Live search (debounced) ───────────────────────────────────────────────
  const runSearch = async (q) => {
    if (!q.trim()) { setSearchResults([]); return }
    setSearching(true); setError('')
    try {
      const res = await searchMovies(q.trim())
      setSearchResults(res.data.results || [])
    } catch {
      setError('Search failed.')
    } finally { setSearching(false) }
  }

  const handleSearchChange = (e) => {
    const val = e.target.value
    setQuery(val)
    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => runSearch(val), 400)
  }

  // ── Tab switch side effects ───────────────────────────────────────────────
  useEffect(() => {
    if (mode === 'dna') loadDna()
    if (mode === 'trending') loadTrending()
  }, [mode])

  useEffect(() => { loadDna() }, [userId])

  // ── Helpers ───────────────────────────────────────────────────────────────
  const activeMovies = mode === 'dna' ? dnaMovies
                     : mode === 'trending' ? trendMovies
                     : searchResults

  const isLoading = mode === 'dna' ? (loadingDna || generatingDna)
                  : mode === 'trending' ? loadingTrend
                  : searching

  return (
    <div className="page discover-page fade-up">

      {/* ── Header ── */}
      <div className="page-header">
        <h1>🎬 <span className="grad-text">Discover</span></h1>
        <p>AI-curated picks powered by your Movie DNA · Live search · Weekly trending</p>
      </div>

      {/* ── Mode Tabs ── */}
      <div className="disc-tabs">
        {MODES.map(m => (
          <button
            key={m.id}
            className={`disc-tab ${mode === m.id ? 'active' : ''}`}
            onClick={() => { setMode(m.id); setError('') }}
          >
            {m.label}
          </button>
        ))}
      </div>

      {/* ── DNA Mode Controls ── */}
      {mode === 'dna' && (
        <div className="disc-controls glass-card">
          <input
            className="input"
            value={dnaQuery}
            onChange={e => setDnaQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && generateDna()}
            placeholder="Refine with a mood or theme… e.g. 'mind-bending sci-fi'"
          />
          <button className="btn btn-primary" onClick={() => generateDna()} disabled={isLoading}>
            {generatingDna ? '⏳ Generating…' : '✨ Generate for Me'}
          </button>
          <button className="btn btn-ghost" onClick={loadDna} disabled={isLoading}>
            ↺ Refresh
          </button>
        </div>
      )}

      {/* ── Search Mode Controls ── */}
      {mode === 'search' && (
        <div className="disc-controls glass-card">
          <div className="search-input-wrap">
            <span className="search-icon">🔍</span>
            <input
              className="input search-input"
              value={query}
              onChange={handleSearchChange}
              placeholder="Type a movie name… e.g. Inception, Interstellar"
              autoFocus
            />
            {searching && <div className="search-spinner" />}
          </div>
        </div>
      )}

      {/* ── Error ── */}
      {error && <div className="alert alert-error">{error}</div>}

      {/* ── Content ── */}
      {isLoading && !activeMovies.length ? (
        <div className="generating-state">
          <div className="spinner" />
          <p>
            {generatingDna ? 'Generating personalised picks via your Movie DNA…' :
             searching ? 'Searching TMDB…' : 'Loading…'}
          </p>
        </div>
      ) : mode === 'search' && !query.trim() ? (
        <div className="disc-search-prompt glass-card">
          <div className="empty-icon">🎬</div>
          <h3>Search any movie</h3>
          <p>Type above to find movies by name, keyword or franchise.</p>
        </div>
      ) : activeMovies.length ? (
        <>
          {/* Section label */}
          <div className="disc-section-label">
            {mode === 'dna' && `🧬 ${dnaMovies.length} DNA-curated picks`}
            {mode === 'trending' && `🔥 ${trendMovies.length} trending this week`}
            {mode === 'search' && `🔍 ${searchResults.length} results for "${query}"`}
          </div>
        <div className="grid-3">
            {activeMovies.map((m, i) => (
              <MovieCard key={m.id || i} movie={m} onClick={setSelectedMovie} />
            ))}
          </div>
        </>
      ) : (
        /* Empty state */
        <div className="empty-state glass-card">
          <div className="empty-icon">{mode === 'dna' ? '🧬' : '🎬'}</div>
          <h3>{mode === 'dna' ? 'No DNA picks yet' : 'No results'}</h3>
          {mode === 'dna' ? (
            <>
              <p>Click <strong>Generate for Me</strong> above to get AI-curated picks.</p>
              <p>Or set up your <a href="/dna" className="link">Movie DNA</a> first for personalised results.</p>
              <button className="btn btn-primary" style={{ marginTop: '16px' }} onClick={() => generateDna('')}>
                ✨ Generate for Me
              </button>
            </>
          ) : (
            <p>No movies found. Try a different search term.</p>
          )}
        </div>
      )}

      {/* Movie Detail Modal */}
      {selectedMovie && (
        <MovieDetailModal
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
        />
      )}
    </div>
  )
}
