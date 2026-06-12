import { useState, useEffect, useRef } from 'react'
import { getChatHistory, streamChat, clearChatHistory } from '../api/client'
import './Chat.css'

/**
 * Markdown → HTML renderer for AI chat bubbles.
 * Order matters: inline spans first, then block structures.
 */
function renderMarkdown(raw) {
  if (!raw) return ''

  // Split into lines for block-level processing
  const lines = raw.split('\n')
  const out = []
  let i = 0

  // ── Inline helpers (applied to a single line of text) ──
  function inline(str) {
    return str
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') // escape
      .replace(/`([^`]+)`/g, '<code class="chat-code">$1</code>')          // `code`
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')                    // **bold**
      .replace(/__(.+?)__/g, '<strong>$1</strong>')                        // __bold__
      .replace(/\*([^*\n]+)\*/g, '<em>$1</em>')                            // *italic*
      .replace(/_([^_\n]+)_/g, '<em>$1</em>')                             // _italic_
  }

  while (i < lines.length) {
    const line = lines[i]

    // H1 / H2 / H3
    if (/^### (.+)/.test(line)) {
      out.push(`<div class="chat-h3">${inline(line.replace(/^### /, ''))}</div>`)
      i++; continue
    }
    if (/^## (.+)/.test(line)) {
      out.push(`<div class="chat-h2">${inline(line.replace(/^## /, ''))}</div>`)
      i++; continue
    }
    if (/^# (.+)/.test(line)) {
      out.push(`<div class="chat-h1">${inline(line.replace(/^# /, ''))}</div>`)
      i++; continue
    }

    // Horizontal rule
    if (/^[-*_]{3,}$/.test(line.trim())) {
      out.push('<div class="chat-hr"></div>')
      i++; continue
    }

    // Blockquote
    if (/^> (.+)/.test(line)) {
      out.push(`<div class="chat-bq">${inline(line.replace(/^> /, ''))}</div>`)
      i++; continue
    }

    // Numbered list — collect consecutive items
    if (/^\d+\.\s/.test(line)) {
      const items = []
      while (i < lines.length && /^\d+\.\s/.test(lines[i])) {
        items.push(`<li class="chat-ol-item">${inline(lines[i].replace(/^\d+\.\s/, ''))}</li>`)
        i++
      }
      out.push(`<ol class="chat-ol">${items.join('')}</ol>`)
      continue
    }

    // Bullet list — collect consecutive items
    if (/^[*-]\s/.test(line)) {
      const items = []
      while (i < lines.length && /^[*-]\s/.test(lines[i])) {
        items.push(`<li class="chat-ul-item">${inline(lines[i].replace(/^[*-]\s/, ''))}</li>`)
        i++
      }
      out.push(`<ul class="chat-ul">${items.join('')}</ul>`)
      continue
    }

    // Blank line → paragraph break
    if (line.trim() === '') {
      out.push('<div class="chat-spacer"></div>')
      i++; continue
    }

    // Plain text paragraph
    out.push(`<p class="chat-p">${inline(line)}</p>`)
    i++
  }

  return out.join('')
}

export default function Chat({ userId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [showQuickPrompts, setShowQuickPrompts] = useState(true)
  const bottomRef = useRef(null)
  const abortRef  = useRef(null)   // holds the abort() fn from streamChat

  const WELCOME = "Hey! I'm your movie companion. Ask me for recommendations, let's talk about a film you love, or I can dig into your taste profile — whatever you're in the mood for."

  useEffect(() => {
    getChatHistory(userId).then(res => {
      if (res.data.history?.length) setMessages(res.data.history)
      else setMessages([{ role: 'assistant', content: WELCOME }])
    }).catch(() => {
      setMessages([{ role: 'assistant', content: WELCOME }])
    })
  }, [userId])

  const stopStreaming = () => {
    abortRef.current?.()     // cancel the fetch stream
    abortRef.current = null
    setStreaming(false)
  }

  const clearChat = async () => {
    stopStreaming()           // stop any in-progress stream first
    try {
      await clearChatHistory(userId)
    } catch { /* ignore */ }
    setMessages([{ role: 'assistant', content: WELCOME }])
    setInput('')
  }

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const sendMessage = () => {
    if (!input.trim() || streaming) return
    const userMsg = { role: 'user', content: input }
    const aiMsg = { role: 'assistant', content: '' }
    setMessages(prev => [...prev, userMsg, aiMsg])
    setInput('')
    setStreaming(true)
    abortRef.current = streamChat(
      userId, input,
      (token) => setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { ...updated[updated.length - 1], content: updated[updated.length - 1].content + token }
        return updated
      }),
      () => { setStreaming(false); abortRef.current = null }
    )
  }

  const quickPrompts = [
    { emoji: '🧬', label: 'Analyse my DNA',         text: '🧬 Analyse my movie DNA' },
    { emoji: '🎬', label: 'Recommend tonight',       text: '🎬 Recommend something for tonight' },
    { emoji: '📈', label: 'Taste evolution',         text: '📈 How has my taste evolved?' },
    { emoji: '🔍', label: 'Movies like Interstellar',text: '🔍 Find movies like Interstellar' },
    { emoji: '🕵️', label: 'Hidden gems',            text: '🕵️ Suggest some hidden gem films' },
    { emoji: '😂', label: 'Feel-good picks',         text: '😂 Recommend feel-good movies for a bad day' },
  ]

  const sendQuickPrompt = (text) => {
    if (streaming) return
    const userMsg = { role: 'user', content: text }
    const aiMsg   = { role: 'assistant', content: '' }
    setMessages(prev => [...prev, userMsg, aiMsg])
    setStreaming(true)
    abortRef.current = streamChat(
      userId, text,
      (token) => setMessages(prev => {
        const updated = [...prev]
        updated[updated.length - 1] = { ...updated[updated.length - 1], content: updated[updated.length - 1].content + token }
        return updated
      }),
      () => { setStreaming(false); abortRef.current = null }
    )
  }

  return (
    <div className="chat-page">
      <div className="chat-header glass-card">
        <div className="chat-avatar">🎬</div>
        <div className="chat-header-meta">
          <h3>CineDNA AI</h3>
          <div className="chat-status">
            <span className={`status-dot ${streaming ? 'thinking' : 'online'}`} />
            <span className="status-text">{streaming ? 'Thinking…' : 'Online'}</span>
          </div>
        </div>
        <button
          className="btn btn-ghost clear-btn"
          onClick={clearChat}
          disabled={streaming}
          title="Clear conversation"
        >
          🗑️ Clear Chat
        </button>
      </div>

      <div className="messages-container">
        {messages.map((m, i) => (
            <div className={`message ${m.role} fade-up`} key={i}>
              {m.role === 'assistant' && <div className="msg-avatar">🤖</div>}
              <div
                className="msg-bubble"
                {...(m.role === 'assistant'
                  ? { dangerouslySetInnerHTML: { __html: renderMarkdown(m.content) || (streaming && i === messages.length - 1 ? '<span class="typing-cursor">▋</span>' : '') } }
                  : { children: m.content }
                )}
              />
            </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* ── Persistent quick-action bar ── */}
      <div className="quick-bar">
        <button
          className="quick-bar-toggle"
          onClick={() => setShowQuickPrompts(v => !v)}
          title={showQuickPrompts ? 'Hide quick actions' : 'Show quick actions'}
        >
          <span className="quick-bar-icon">⚡</span>
          <span>Quick Actions</span>
          <span className="quick-bar-chevron">{showQuickPrompts ? '▴' : '▾'}</span>
        </button>

        {showQuickPrompts && (
          <div className="quick-prompts">
            {quickPrompts.map(p => (
              <button
                key={p.text}
                className={`quick-btn ${streaming ? 'quick-btn--disabled' : ''}`}
                onClick={() => sendQuickPrompt(p.text)}
                disabled={streaming}
              >
                <span className="quick-btn-emoji">{p.emoji}</span>
                {p.label}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="chat-input-bar glass-card">
        <textarea
          className="chat-textarea"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())}
          placeholder="Ask about movies, your taste, recommendations…"
          rows={1}
        />
        {streaming ? (
          <button className="btn stop-btn" onClick={stopStreaming} title="Stop generation">
            ⏹ Stop
          </button>
        ) : (
          <button className="btn btn-primary send-btn" onClick={sendMessage} disabled={!input.trim()}>
            ➤
          </button>
        )}
      </div>
    </div>
  )
}
