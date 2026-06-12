import './MovieCard.css'

const TMDB_IMAGE_BASE = 'https://image.tmdb.org/t/p/w500'

function getPosterUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `${TMDB_IMAGE_BASE}${path}`
}

export default function MovieCard({ movie, onRate, onClick }) {
  const rating = movie.vote_average?.toFixed(1) || '?'
  const year = movie.release_date?.slice(0, 4) || ''
  const posterUrl = getPosterUrl(movie.poster_path)
  const genres = movie.genres || []

  return (
    <div
      className={`movie-card glass-card${onClick ? ' movie-card--clickable' : ''}`}
      onClick={onClick ? () => onClick(movie) : undefined}
    >
      <div className="movie-poster">
        {posterUrl ? (
          <img src={posterUrl} alt={movie.title} loading="lazy" />
        ) : (
          <div className="poster-placeholder">
            <span className="poster-icon">🎬</span>
            <span className="poster-title-fallback">{movie.title}</span>
          </div>
        )}
        <div className="movie-rating-badge">⭐ {rating}</div>
        {year && <div className="movie-year-badge">{year}</div>}
      </div>
      <div className="movie-info">
        <h3 className="movie-title">{movie.title}</h3>
        {genres.length > 0 && (
          <div className="movie-genres">
            {genres.slice(0, 2).map(g => (
              <span key={g.id || g} className="movie-genre-tag">{g.name || g}</span>
            ))}
          </div>
        )}
        {movie.overview && (
          <p className="movie-overview">{movie.overview.slice(0, 110)}…</p>
        )}
        {movie.reason && (
          <p className="movie-reason">
            <span className="reason-icon">🧬</span> {movie.reason}
          </p>
        )}
        {onRate && (
          <button className="btn btn-ghost btn-sm" onClick={() => onRate(movie)}>
            Rate
          </button>
        )}
      </div>
    </div>
  )
}
