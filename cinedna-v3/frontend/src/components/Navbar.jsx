import { NavLink } from 'react-router-dom'
import './Navbar.css'

const links = [
  { to: '/', label: '🏠 Home' },
  { to: '/dna', label: '🧬 Movie DNA' },
  { to: '/chat', label: '💬 Chat' },
  { to: '/recommendations', label: '🎬 Discover' },
  { to: '/profile', label: '👤 Profile' },
]

export default function Navbar() {
  return (
    <nav className="navbar">
      <NavLink to="/" className="navbar-brand">
        <span className="brand-icon">🎬</span>
        <span className="brand-name">Cine<span className="grad-text">DNA</span></span>
      </NavLink>
      <div className="navbar-links">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === '/'}
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            {l.label}
          </NavLink>
        ))}
      </div>
    </nav>
  )
}
