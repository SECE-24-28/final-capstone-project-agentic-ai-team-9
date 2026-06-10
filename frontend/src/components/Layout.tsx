import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Film, Sparkles, User, LogOut } from 'lucide-react';
import { useStore } from '../store/useStore';

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const isLanding = location.pathname === '/';
  const { profile, clearProfile } = useStore();

  return (
    <div className="min-h-screen relative overflow-x-hidden flex flex-col">
      {/* Background Effects */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary-500/20 rounded-full blur-[120px] animate-blob"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-500/20 rounded-full blur-[120px] animate-blob animation-delay-2000"></div>
        <div className="absolute top-[40%] left-[60%] w-[30%] h-[30%] bg-purple-500/20 rounded-full blur-[100px] animate-blob animation-delay-4000"></div>
      </div>

      {/* Navbar */}
      {!isLanding && (
        <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-dark-900/50 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link to="/" className="flex items-center gap-2 group">
                <Film className="w-6 h-6 text-primary-400 group-hover:text-primary-300 transition-colors" />
                <span className="font-bold text-xl tracking-tight text-white group-hover:text-gray-200 transition-colors">
                  CineDNA
                </span>
              </Link>
              
              {profile && (
                <div className="flex items-center gap-4">
                  <Link to="/dashboard" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2 text-sm font-medium">
                    <Sparkles className="w-4 h-4" />
                    Dashboard
                  </Link>
                  <button 
                    onClick={clearProfile}
                    className="text-gray-400 hover:text-primary-400 transition-colors"
                    title="Retake DNA Analysis"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </nav>
      )}

      {/* Main Content */}
      <main className="flex-grow relative z-10 w-full">
        {children}
      </main>
    </div>
  );
}
