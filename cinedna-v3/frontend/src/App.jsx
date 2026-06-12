import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import MovieDNA from './pages/MovieDNA'
import Chat from './pages/Chat'
import Recommendations from './pages/Recommendations'
import Profile from './pages/Profile'

const USER_ID = 'default_user'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dna" element={<MovieDNA userId={USER_ID} />} />
          <Route path="/chat" element={<Chat userId={USER_ID} />} />
          <Route path="/recommendations" element={<Recommendations userId={USER_ID} />} />
          <Route path="/profile" element={<Profile userId={USER_ID} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
