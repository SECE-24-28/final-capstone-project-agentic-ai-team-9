import React, { useState, useRef, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { BrainCircuit, Fingerprint, Eye, History, Send, Play, Bot, User, Loader2 } from 'lucide-react';
import { useStore } from '../store/useStore';
import axios from 'axios';

export default function Dashboard() {
  const { profile, userId } = useStore();
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initial welcome message
  useEffect(() => {
    if (profile && messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: `Your Movie DNA is active. I see you're a **${profile.soul_profile.split('—')[0].trim()}**. How can I assist you today? Ask for recommendations or explore your hidden tastes.`
      }]);
    }
  }, [profile]);

  if (!profile) {
    return <Navigate to="/onboarding" />;
  }

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim() || isTyping) return;

    const userMsg = query;
    setQuery('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setIsTyping(true);

    try {
      // In a real app, this would use a streaming endpoint
      const response = await axios.post('http://localhost:8000/api/chat', {
        user_id: userId,
        query: userMsg,
        profile: profile
      });
      
      setMessages(prev => [...prev, { role: 'assistant', content: response.data.reply }]);
    } catch (error) {
      console.error(error);
      // Fallback response for UI
      setTimeout(() => {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: "🎬 **Dune: Part Two** (2024)\nWhy: It matches your love for epic world-building and visionary storytelling, perfectly aligning with your Cosmic Visionary soul."
        }]);
      }, 1500);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-8 h-[calc(100vh-64px)]">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full">
        
        {/* Left Sidebar: DNA Profile */}
        <div className="lg:col-span-3 lg:col-start-1 flex flex-col gap-6 overflow-y-auto pr-2 pb-8">
          <div className="glass-card p-6 border-t-4 border-t-primary-500">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-primary-500/20 rounded-lg">
                <BrainCircuit className="w-5 h-5 text-primary-400" />
              </div>
              <h3 className="font-bold text-gray-200 tracking-wider text-xs uppercase">Soul Type</h3>
            </div>
            <p className="text-white font-medium leading-relaxed">
              {profile.soul_profile}
            </p>
          </div>

          <div className="glass-card p-6 border-t-4 border-t-blue-500">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Fingerprint className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="font-bold text-gray-200 tracking-wider text-xs uppercase">Character DNA</h3>
            </div>
            <p className="text-white font-medium leading-relaxed">
              {profile.character_dna}
            </p>
          </div>

          <div className="glass-card p-6 border-t-4 border-t-purple-500">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-500/20 rounded-lg">
                <Eye className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="font-bold text-gray-200 tracking-wider text-xs uppercase">Hidden Taste</h3>
            </div>
            <p className="text-white font-medium leading-relaxed">
              {profile.hidden_taste}
            </p>
          </div>

          {profile.taste_evolution && (
            <div className="glass-card p-6 border-t-4 border-t-yellow-500 bg-gradient-to-b from-yellow-500/5 to-transparent">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-yellow-500/20 rounded-lg">
                  <History className="w-5 h-5 text-yellow-400" />
                </div>
                <h3 className="font-bold text-gray-200 tracking-wider text-xs uppercase">Taste Evolution</h3>
              </div>
              <p className="text-white font-medium leading-relaxed">
                {profile.taste_evolution}
              </p>
            </div>
          )}
        </div>

        {/* Main Chat Area */}
        <div className="lg:col-span-9 flex flex-col h-full glass-card overflow-hidden">
          {/* Quick Actions Header */}
          <div className="p-4 border-b border-white/10 bg-black/20 flex gap-3 overflow-x-auto whitespace-nowrap">
            {['Recommend me 3 movies', 'Explore my hidden taste', 'Explain my Character DNA'].map((action, i) => (
              <button 
                key={i}
                onClick={() => {
                  setQuery(action);
                  setTimeout(() => document.getElementById('chat-input')?.focus(), 10);
                }}
                className="px-4 py-2 rounded-full border border-white/10 bg-white/5 hover:bg-white/10 text-sm font-medium text-gray-300 transition-colors"
              >
                {action}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((msg, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 max-w-[85%] ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === 'user' ? 'bg-primary-500' : 'bg-dark-700 border border-white/10'
                }`}>
                  {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-primary-400" />}
                </div>
                
                <div className={`p-4 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-primary-500/20 border border-primary-500/30 text-white rounded-tr-sm' 
                    : 'glass-card border-white/10 rounded-tl-sm'
                }`}>
                  <div className="prose prose-invert max-w-none text-sm md:text-base leading-relaxed">
                    {/* Simplified markdown rendering for demo */}
                    {msg.content.split('\n').map((line, i) => (
                      <p key={i} className={line.startsWith('🎬') ? 'font-bold text-primary-300 mt-4 mb-1' : 'my-1'}>
                        {line}
                      </p>
                    ))}
                  </div>
                  
                  {/* Mock TMDB Integration for assistant responses */}
                  {msg.role === 'assistant' && msg.content.includes('🎬') && (
                    <div className="mt-4 flex gap-3">
                      <button className="flex items-center gap-1.5 px-3 py-1.5 bg-primary-500/20 text-primary-400 text-xs font-bold rounded-lg hover:bg-primary-500/30 transition-colors">
                        <Play className="w-3 h-3" /> Trailer
                      </button>
                      <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 text-gray-300 text-xs font-bold rounded-lg hover:bg-white/10 transition-colors border border-white/10">
                        + Watchlist
                      </button>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            
            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 max-w-[85%]">
                <div className="w-8 h-8 rounded-full bg-dark-700 border border-white/10 flex items-center justify-center shrink-0">
                  <Bot className="w-4 h-4 text-primary-400" />
                </div>
                <div className="glass-card border-white/10 rounded-tl-sm rounded-2xl p-4 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-primary-400 animate-spin" />
                  <span className="text-sm text-gray-400 font-medium">Qwen3 is thinking...</span>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 border-t border-white/10 bg-black/20">
            <form onSubmit={handleSend} className="relative flex items-center">
              <input 
                id="chat-input"
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask about movies, directors, or explore your DNA..."
                className="w-full bg-dark-900/50 border border-white/10 rounded-xl pl-4 pr-12 py-4 text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500/50 backdrop-blur-md transition-all"
                disabled={isTyping}
              />
              <button 
                type="submit"
                disabled={!query.trim() || isTyping}
                className="absolute right-2 p-2 bg-primary-500 hover:bg-primary-400 disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-lg transition-colors"
              >
                <Send className="w-5 h-5 ml-0.5" />
              </button>
            </form>
            <div className="text-center mt-2">
              <span className="text-[10px] text-gray-500 uppercase tracking-widest font-bold">Powered by Qwen3 via Ollama</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
