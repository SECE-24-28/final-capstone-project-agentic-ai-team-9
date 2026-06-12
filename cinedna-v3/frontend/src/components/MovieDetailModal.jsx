import { useEffect, useState } from 'react'
import { getMovieDetail } from '../api/client'
import './MovieDetailModal.css'

const TMDB_IMG = 'https://image.tmdb.org/t/p/w500'
const TMDB_BACKDROP = 'https://image.tmdb.org/t/p/w1280'

function imgUrl(path, base = TMDB_IMG) {
  if (!path) return null
  return path.startsWith('http') ? path : `${base}${path}`
}

export default function MovieDetailModal({ movie, onClose }) {
  const [detail, setDetail]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  /* Fetch full details */
  useEffect(() => {
    if (!movie?.id) return
    setLoading(true); setError(''); setDetail(null)

    getMovieDetail(movie.id)
      .then(res => setDetail(res.data))
      .catch(() => setError('Could not load movie details.'))
      .finally(() => setLoading(false))
  }, [movie?.id])

  /* Close on Escape */
  useEffect(() => {
    const handler = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  /* Prevent body scroll */
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = '' }
  }, [])

  const data = detail || movie        // use card data while loading
  const backdropUrl = imgUrl(data?.backdrop_path, TMDB_BACKDROP)
  const posterUrl   = imgUrl(data?.poster_path)
  const year        = data?.release_date?.slice(0, 4)
  const rating      = data?.vote_average?.toFixed(1)
  const genres      = detail?.genres || []
  const cast        = detail?.cast || []
  const director    = detail?.director
  const keywords    = detail?.keywords?.slice(0, 8) || []

  return (
    <div className="mdm-overlay" onClick={onClose}>
      <div className="mdm-panel glass-card" onClick={e => e.stopPropagation()}>

        {/* ── Backdrop ── */}
        <div className="mdm-backdrop" style={backdropUrl ? { backgroundImage: `url(${backdropUrl})` } : {}}>
          <div className="mdm-backdrop-grad" />
          <button className="mdm-close" onClick={onClose} aria-label="Close">✕</button>
        </div>

        {/* ── Body ── */}
        <div className="mdm-body">

          {/* Poster + meta */}
          <div className="mdm-top">
            <div className="mdm-poster-wrap">
              {posterUrl
                ? <img className="mdm-poster" src={posterUrl} alt={data?.title} />
                : <div className="mdm-poster-placeholder">🎬</div>
              }
            </div>

            <div className="mdm-meta">
              <h2 className="mdm-title">{data?.title}</h2>
              <div className="mdm-badges">
                {year && <span className="mdm-badge">{year}</span>}
                {rating && rating !== '0.0' && (
                  <span className="mdm-badge mdm-badge--gold">⭐ {rating}</span>
                )}
                {director && <span className="mdm-badge mdm-badge--purple">🎬 {director}</span>}
              </div>

              {/* Genres */}
              {genres.length > 0 && (
                <div className="mdm-genres">
                  {genres.map(g => (
                    <span key={g.id} className="mdm-genre-tag">{g.name}</span>
                  ))}
                </div>
              )}

              {/* Overview */}
              {data?.overview && (
                <p className="mdm-overview">{data.overview}</p>
              )}

              {loading && !detail && (
                <div className="mdm-loading">
                  <div className="spinner" style={{ margin: '16px 0', width: 28, height: 28, borderWidth: 2 }} />
                  <span>Loading full details…</span>
                </div>
              )}
              {error && <div className="alert alert-error" style={{ marginTop: 12 }}>{error}</div>}
            </div>
          </div>

          {/* Cast */}
          {cast.length > 0 && (
            <div className="mdm-section">
              <div className="mdm-section-title">🎭 Cast</div>
              <div className="mdm-cast-list">
                {cast.map((a, i) => (
                  <div key={i} className="mdm-cast-item">
                    <div className="mdm-cast-avatar">{a.name?.[0]}</div>
                    <div>
                      <div className="mdm-cast-name">{a.name}</div>
                      <div className="mdm-cast-char">{a.character}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Keywords */}
          {keywords.length > 0 && (
            <div className="mdm-section">
              <div className="mdm-section-title">🏷️ Themes & Keywords</div>
              <div className="mdm-keywords">
                {keywords.map(k => (
                  <span key={k} className="mdm-keyword">{k}</span>
                ))}
              </div>
            </div>
          )}

          {/* DNA reason if present */}
          {data?.reason && (
            <div className="mdm-reason">
              <span>🧬</span> {data.reason}
            </div>
          )}

        </div>
      </div>
    </div>
  )
}
