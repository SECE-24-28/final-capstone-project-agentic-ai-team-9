import { useState, useEffect } from 'react'
import { getProfile, getRatings, getTasteEvolution, analyzeEvolution } from '../api/client'
import './Profile.css'

export default function Profile({ userId }) {
  const [profile, setProfile] = useState(null)
  const [ratings, setRatings] = useState([])
  const [evolution, setEvolution] = useState([])
  const [analyzing, setAnalyzing] = useState(false)
  const [tab, setTab] = useState('dna')

  useEffect(() => {
    getProfile(userId).then(r => setProfile(r.data)).catch(() => {})
    getRatings(userId).then(r => setRatings(r.data.ratings || [])).catch(() => {})
    getTasteEvolution(userId).then(r => setEvolution(r.data.evolution || [])).catch(() => {})
  }, [userId])

  const handleAnalyze = async () => {
    setAnalyzing(true)
    try {
      await analyzeEvolution(userId)
      const r = await getTasteEvolution(userId)
      setEvolution(r.data.evolution || [])
    } finally { setAnalyzing(false) }
  }

  return (
    <div className="page profile-page fade-up">
      <div className="page-header">
        <h1>👤 <span className="grad-text">My Profile</span></h1>
        <p>Your CineDNA, ratings, and taste evolution.</p>
      </div>

      <div className="profile-tabs">
        {['dna', 'ratings', 'evolution'].map(t => (
          <button key={t} className={`tab-btn ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
            {t === 'dna' ? '🧬 DNA' : t === 'ratings' ? '⭐ Ratings' : '📈 Evolution'}
          </button>
        ))}
      </div>

      {tab === 'dna' && (
        profile ? (
          <div className="profile-dna">
            <div className="dna-section glass-card">
              <h3>🔮 Soul Type</h3>
              <p>{profile.soul_profile || 'Not generated yet.'}</p>
            </div>
            <div className="dna-section glass-card">
              <h3>🎭 Character DNA</h3>
              <p>{profile.character_dna || 'Not generated yet.'}</p>
            </div>
            <div className="dna-section glass-card">
              <h3>🕵️ Hidden Taste</h3>
              <p>{profile.hidden_taste || 'Not generated yet.'}</p>
            </div>
            <div className="profile-lists glass-card">
              <div className="profile-list">
                <p className="section-title">Favorite Movies</p>
                <div className="tags-row">{(profile.favorite_movies || []).map(m => <span key={m} className="tag">{m}</span>)}</div>
              </div>
              <div className="profile-list">
                <p className="section-title">Favorite Genres</p>
                <div className="tags-row">{(profile.favorite_genres || []).map(g => <span key={g} className="tag">{g}</span>)}</div>
              </div>
              <div className="profile-list">
                <p className="section-title">Favorite Characters</p>
                <div className="tags-row">{(profile.favorite_characters || []).map(c => <span key={c} className="tag">{c}</span>)}</div>
              </div>
            </div>
          </div>
        ) : <div className="alert alert-info">No DNA profile yet. <a href="/dna" className="link">Create yours →</a></div>
      )}

      {tab === 'ratings' && (
        <div className="ratings-list">
          {ratings.length ? ratings.map((r, i) => (
            <div key={i} className="rating-row glass-card">
              <div className="rating-title">{r.movie_title}</div>
              <div className="rating-score">⭐ {r.rating}/10</div>
              {r.review && <p className="rating-review">{r.review}</p>}
              <span className="rating-date">{r.rated_at?.slice(0, 10)}</span>
            </div>
          )) : <div className="alert alert-info">No ratings yet. Rate movies from the Discover page!</div>}
        </div>
      )}

      {tab === 'evolution' && (
        <div className="evolution-section">
          <button className="btn btn-primary" onClick={handleAnalyze} disabled={analyzing} style={{marginBottom:'20px'}}>
            {analyzing ? '⏳ Analysing…' : '🔬 Run Taste Analysis'}
          </button>
          {evolution.length ? evolution.map((e, i) => (
            <div key={i} className="evolution-card glass-card">
              <div className="evolution-date">{e.created_at?.slice(0, 10)}</div>
              <p>{e.analysis}</p>
            </div>
          )) : <div className="alert alert-info">No evolution snapshots yet. Click "Run Taste Analysis" above!</div>}
        </div>
      )}
    </div>
  )
}
