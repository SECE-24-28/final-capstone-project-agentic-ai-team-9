import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronRight, Play, Sparkles, Brain, Compass } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center relative overflow-hidden">
      
      {/* Aurora Background */}
      <div className="absolute inset-0 z-0 opacity-40">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary-500/30 rounded-full mix-blend-screen filter blur-[100px] animate-blob"></div>
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-blue-500/30 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-purple-500/30 rounded-full mix-blend-screen filter blur-[100px] animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center mt-20">
        
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card text-sm font-medium text-primary-300 mb-8">
            <Sparkles className="w-4 h-4" />
            V2 Now Available with LangChain & Qwen3
          </span>
          
          <h1 className="text-6xl md:text-8xl font-black tracking-tight mb-8">
            Discover Your <br />
            <span className="gradient-text">Movie Soul</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-400 max-w-3xl mx-auto mb-12 leading-relaxed">
            An intelligent AI companion that understands your cinematic personality. Stop scrolling through endless catalogs and start discovering films meant for you.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button 
              onClick={() => navigate('/onboarding')}
              className="w-full sm:w-auto px-8 py-4 bg-primary-500 hover:bg-primary-400 text-white rounded-2xl font-bold text-lg transition-all shadow-[0_0_40px_rgba(233,69,96,0.4)] hover:shadow-[0_0_60px_rgba(233,69,96,0.6)] hover:-translate-y-1 flex items-center justify-center gap-2"
            >
              Analyze My Movie DNA
              <ChevronRight className="w-5 h-5" />
            </button>
            
            <button className="w-full sm:w-auto px-8 py-4 glass-button text-white rounded-2xl font-medium text-lg">
              <Play className="w-5 h-5" />
              Watch Demo
            </button>
          </div>
        </motion.div>

        {/* Feature Grid */}
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-32 mb-20 text-left"
        >
          {[
            {
              icon: <Brain className="w-6 h-6 text-primary-400" />,
              title: "Psychological Profiling",
              desc: "Analyzes your favorite films to build a deep Character DNA and Soul Profile."
            },
            {
              icon: <Sparkles className="w-6 h-6 text-blue-400" />,
              title: "Hidden Taste Discovery",
              desc: "Uncovers sub-genres and niche categories you didn't even know you loved."
            },
            {
              icon: <Compass className="w-6 h-6 text-purple-400" />,
              title: "Agentic Recommendations",
              desc: "Real-time, context-aware suggestions powered by local Qwen3 AI and TMDB."
            }
          ].map((feat, i) => (
            <div key={i} className="glass-card p-8 group hover:border-primary-500/50 transition-colors">
              <div className="bg-white/5 rounded-xl w-12 h-12 flex items-center justify-center mb-6 border border-white/10 group-hover:scale-110 transition-transform">
                {feat.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-3">{feat.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feat.desc}</p>
            </div>
          ))}
        </motion.div>

      </div>
    </div>
  );
}
