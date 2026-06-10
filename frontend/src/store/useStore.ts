import { create } from 'zustand';

interface UserProfile {
  soul_profile: string;
  character_dna: string;
  hidden_taste: string;
  taste_evolution?: string;
  favorite_movies: string;
  favorite_characters: string;
  favorite_genres: string;
}

interface AppState {
  userId: string;
  profile: UserProfile | null;
  setProfile: (profile: UserProfile) => void;
  clearProfile: () => void;
  onboardingStep: number;
  setOnboardingStep: (step: number) => void;
}

export const useStore = create<AppState>((set) => ({
  userId: 'guest_user',
  profile: null,
  setProfile: (profile) => set({ profile }),
  clearProfile: () => set({ profile: null, onboardingStep: 1 }),
  onboardingStep: 1,
  setOnboardingStep: (step) => set({ onboardingStep: step }),
}));
