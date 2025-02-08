import { create } from 'zustand';
import { AIAgent, MarketplaceFilters } from '@/types/marketplace';

interface MarketplaceState {
  // State
  agents: AIAgent[];
  isLoading: boolean;
  error: string | null;
  filters: MarketplaceFilters;
  
  // Actions
  setAgents: (agents: AIAgent[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setFilter: <K extends keyof MarketplaceFilters>(
    key: K,
    value: MarketplaceFilters[K]
  ) => void;
  resetFilters: () => void;
}

const initialFilters: MarketplaceFilters = {
  search: '',
  category: 'All',
  sortBy: 'latest',
  priceRange: {
    min: 0,
    max: 10,
  },
  page: 1,
};

export const useMarketplaceStore = create<MarketplaceState>((set) => ({
  // Initial state
  agents: [],
  isLoading: false,
  error: null,
  filters: initialFilters,

  // Actions
  setAgents: (agents) => set({ agents }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  setFilter: (key, value) =>
    set((state) => ({
      filters: {
        ...state.filters,
        [key]: value,
      },
    })),
    
  resetFilters: () => set({ filters: initialFilters }),
}));