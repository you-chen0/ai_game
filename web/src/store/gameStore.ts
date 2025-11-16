import { create } from 'zustand';
import { GameStore } from '@/types/story';

export const useGameStore = create<GameStore>((set) => ({
  phase: 'upload',
  currentState: null,
  isLoading: false,
  error: null,
  imageFile: null,
  imageUrl: null,
  stateId: null,

  setPhase: (phase) => set({ phase }),

  setCurrentState: (currentState) => set({ currentState }),

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),

  setImageFile: (imageFile) => set({ imageFile }),

  setImageUrl: (imageUrl) => set({ imageUrl }),

  setStateId: (stateId) => set({ stateId }),

  reset: () => set({
    phase: 'upload',
    currentState: null,
    isLoading: false,
    error: null,
    imageFile: null,
    imageUrl: null,
    stateId: null,
  }),
}));
