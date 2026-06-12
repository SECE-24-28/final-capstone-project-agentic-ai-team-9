import axios from 'axios'

const API = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

// DNA
export const generateDNA = (data) => API.post('/dna/generate', data)
export const getDNA = (userId) => API.get(`/dna/${userId}`)
export const regenerateDNA = (userId) => API.post(`/dna/regenerate/${userId}`)

// Recommendations
export const getRecommendations = (userId) => API.get(`/recommendations/${userId}`)
export const generateRecommendations = (data) => API.post('/recommendations/generate', data)
export const getTrending = () => API.get('/recommendations/trending/now')
export const searchMovies = (q) => API.get('/recommendations/search', { params: { q } })

// Movie detail
export const getMovieDetail = (movieId) => API.get(`/movie/${movieId}`)

// Profile
export const getProfile = (userId) => API.get(`/profile/${userId}`)
export const updateProfile = (userId, data) => API.put(`/profile/${userId}`, data)
export const rateMovie = (userId, data) => API.post(`/profile/${userId}/rate`, data)
export const getRatings = (userId) => API.get(`/profile/${userId}/ratings`)
export const getTasteEvolution = (userId) => API.get(`/profile/${userId}/evolution`)
export const analyzeEvolution = (userId) => API.post(`/profile/${userId}/evolution/analyze`)

// Chat history
export const getChatHistory = (userId) => API.get(`/chat/history/${userId}`)
export const clearChatHistory = (userId) => API.delete(`/chat/history/${userId}`)

// Streaming chat (SSE) — returns abort() function
export const streamChat = (userId, message, onToken, onDone) => {
  const controller = new AbortController()

  fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, message, stream: true }),
    signal: controller.signal,
  }).then(async (res) => {
    const reader = res.body.getReader()
    const decoder = new TextDecoder()
    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value)
        const lines = text.split('\n').filter((l) => l.startsWith('data:'))
        for (const line of lines) {
          const data = line.slice(5).trim()
          if (data === '[DONE]') { onDone?.(); return }
          try {
            const parsed = JSON.parse(data)
            if (parsed.token) onToken(parsed.token)
          } catch {}
        }
      }
    } catch (err) {
      if (err.name !== 'AbortError') console.error('Stream error:', err)
    } finally {
      onDone?.()
    }
  }).catch((err) => {
    if (err.name !== 'AbortError') console.error('Fetch error:', err)
    onDone?.()
  })

  return () => controller.abort()
}

export default API
