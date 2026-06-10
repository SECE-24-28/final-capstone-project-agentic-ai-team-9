import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, Film, Users, Clapperboard, Sparkles } from 'lucide-react';
import { useStore } from '../store/useStore';
import axios from 'axios';

const steps = [
  { id: 1, title: 'Favorite Movies', icon: Film, subtitle: 'These form the core of your Movie DNA' },
  { id: 2, title: 'Favorite Characters', icon: Users, subtitle: 'Reveals your personality DNA' },
  { id: 3, title: 'Favorite Genres', icon: Clapperboard, subtitle: 'Unlocks hidden taste discoveries' },
];

export default function OnboardingWizard() {
  const navigate = useNavigate();
  const { onboardingStep, setOnboardingStep, setProfile } = useStore();
  
  const [movies, setMovies] = useState('');
  const [characters, setCharacters] = useState('');
  const [genres, setGenres] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleNext = () => {
    if (onboardingStep < 3) {
      setOnboardingStep(onboardingStep + 1);
    } else {
      generateDNA();
    }
  };

  const handleBack = () => {
    if (onboardingStep > 1) {
      setOnboardingStep(onboardingStep - 1);
    } else {
      navigate('/');
    }
  };

  const generateDNA = async () => {
    setIsGenerating(true);
    try {
      // Setup backend API call to FastAPI
      const response = await axios.post('http://localhost:8000/api/generate-dna', {
        movies, characters, genres
      });
      setProfile(response.data);
      navigate('/dashboard');
    } catch (error) {
      console.error('Error generating DNA', error);
      // Fallback for UI testing
      setTimeout(() => {
        setProfile({
          soul_profile: 'The Cosmic Visionary',
          character_dna: 'Intellectual and ambitious',
          hidden_taste: 'Neo-noir sci-fi',
          favorite_movies: movies,
          favorite_characters: characters,
          favorite_genres: genres
        });
        setIsGenerating(false);
        navigate('/dashboard');
      }, 3000);
    }
  };

  if (isGenerating) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center relative">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative w-32 h-32 mx-auto mb-8">
            <div className="absolute inset-0 border-4 border-primary-500/20 rounded-full animate-spin"></div>
            <div className="absolute inset-0 border-4 border-primary-500 rounded-full border-t-transparent animate-spin animation-delay-150"></div>
            <Sparkles className="absolute inset-0 m-auto w-10 h-10 text-primary-400 animate-pulse" />
          </div>
          <h2 className="text-3xl font-bold text-white mb-4">Sequencing your Movie DNA...</h2>
          <p className="text-gray-400">Our AI is analyzing your cinematic personality.</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Progress Bar */}
        <div className="flex justify-between items-center mb-12">
          {steps.map((step) => (
            <div key={step.id} className="flex flex-col items-center relative z-10">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-colors duration-500 ${
                step.id === onboardingStep 
                  ? 'bg-primary-500 border-primary-500 text-white shadow-[0_0_20px_rgba(233,69,96,0.5)]' 
                  : step.id < onboardingStep
                    ? 'bg-primary-500/20 border-primary-500 text-primary-400'
                    : 'bg-dark-800 border-white/10 text-gray-500'
              }`}>
                <step.icon className="w-5 h-5" />
              </div>
              <span className={`absolute -bottom-6 text-xs font-medium whitespace-nowrap transition-colors duration-500 ${
                step.id <= onboardingStep ? 'text-primary-300' : 'text-gray-500'
              }`}>
                {step.title}
              </span>
            </div>
          ))}
          <div className="absolute left-0 top-6 w-full h-[2px] bg-white/5 -z-10 px-6">
            <motion.div 
              className="h-full bg-gradient-to-r from-primary-500 to-primary-400"
              initial={{ width: '0%' }}
              animate={{ width: `${((onboardingStep - 1) / 2) * 100}%` }}
              transition={{ duration: 0.5, ease: 'easeInOut' }}
            />
          </div>
        </div>

        {/* Wizard Card */}
        <motion.div 
          key={onboardingStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="glass-card p-8 md:p-12 mt-10"
        >
          <div className="text-center mb-10">
            <span className="text-primary-400 font-bold tracking-wider text-sm uppercase">Step {onboardingStep} of 3</span>
            <h2 className="text-3xl md:text-4xl font-bold text-white mt-2 mb-3">{steps[onboardingStep-1].title}</h2>
            <p className="text-gray-400">{steps[onboardingStep-1].subtitle}</p>
          </div>

          <div className="space-y-6">
            {onboardingStep === 1 && (
              <input 
                type="text" 
                value={movies}
                onChange={(e) => setMovies(e.target.value)}
                placeholder="e.g. Interstellar, The Matrix, Inception" 
                className="premium-input text-lg"
                autoFocus
              />
            )}
            {onboardingStep === 2 && (
              <input 
                type="text" 
                value={characters}
                onChange={(e) => setCharacters(e.target.value)}
                placeholder="e.g. Tony Stark, Ellen Ripley, Neo" 
                className="premium-input text-lg"
                autoFocus
              />
            )}
            {onboardingStep === 3 && (
              <input 
                type="text" 
                value={genres}
                onChange={(e) => setGenres(e.target.value)}
                placeholder="e.g. Sci-Fi, Psychological Thriller" 
                className="premium-input text-lg"
                autoFocus
              />
            )}
          </div>

          <div className="flex justify-between items-center mt-12 pt-8 border-t border-white/10">
            <button 
              onClick={handleBack}
              className="px-6 py-3 text-gray-400 hover:text-white transition-colors flex items-center gap-2 font-medium"
            >
              <ChevronLeft className="w-5 h-5" />
              {onboardingStep === 1 ? 'Cancel' : 'Back'}
            </button>
            <button 
              onClick={handleNext}
              className="px-8 py-3 bg-primary-500 hover:bg-primary-400 text-white rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(233,69,96,0.3)] hover:shadow-[0_0_30px_rgba(233,69,96,0.5)] flex items-center gap-2"
            >
              {onboardingStep === 3 ? 'Analyze DNA' : 'Continue'}
              {onboardingStep < 3 && <ChevronRight className="w-5 h-5" />}
              {onboardingStep === 3 && <Sparkles className="w-5 h-5" />}
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
