import { useNavigate } from 'react-router-dom'
import './Landing.css'

const features = [
  { icon: '🧬', title: 'Movie DNA', desc: 'Deep psychological profiling of your cinematic soul.' },
  { icon: '🤖', title: 'Agentic AI', desc: 'LangChain + Qwen3 with ReAct reasoning and MCP tools.' },
  { icon: '🔍', title: 'RAG Search', desc: 'ChromaDB vector search finds movies that match your essence.' },
  { icon: '📡', title: 'MCP Server', desc: 'Expose CineDNA tools to any MCP-compatible AI client.' },
  { icon: '🎯', title: 'Taste Evolution', desc: 'Watch your taste transform movie by movie.' },
  { icon: '🔒', title: 'Fully Local', desc: 'Zero cloud. Qwen3 runs on your machine via Ollama.' },
]

export default function Landing() {
  const navigate = useNavigate()
  return (
    <div className="landing">
      <div className="landing-bg" />
      <section className="hero fade-up">
        <div className="hero-badge badge">✨ Powered by Qwen3 + LangChain + ChromaDB</div>
        <h1>Your <span className="grad-text">Cinematic DNA</span><br />Decoded by AI</h1>
        <p className="hero-sub">
          CineDNA is a production-grade Agentic AI companion that builds a deep psychological
          profile of your movie taste — then finds films that speak to your soul.
        </p>
        <div className="hero-actions">
          <button className="btn btn-primary btn-lg" onClick={() => navigate('/dna')}>
            🧬 Discover Your DNA
          </button>
          <button className="btn btn-ghost btn-lg" onClick={() => navigate('/chat')}>
            💬 Chat with AI
          </button>
        </div>
        <div className="hero-stats">
          <div className="stat"><span className="stat-num">MCP</span><span>Protocol</span></div>
          <div className="stat-div" />
          <div className="stat"><span className="stat-num">RAG</span><span>Pipeline</span></div>
          <div className="stat-div" />
          <div className="stat"><span className="stat-num">100%</span><span>Local AI</span></div>
        </div>
      </section>

      <section className="features page">
        <p className="section-title">Core Capabilities</p>
        <div className="grid-3">
          {features.map((f, i) => (
            <div key={i} className="feature-card glass-card fade-up" style={{ animationDelay: `${i * 0.08}s` }}>
              <div className="feature-icon">{f.icon}</div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
