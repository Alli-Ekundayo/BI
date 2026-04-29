import { create } from "zustand";
import type { QueryResponse } from "../types";

interface QueryState {
  latestResult: QueryResponse | null;
  history: QueryResponse[];
  isLoading: boolean;
  error: string | null;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addResult: (result: QueryResponse) => void;
  selectResult: (result: QueryResponse) => void;
  clearResults: () => void;
}

export const useQueryStore = create<QueryState>((set) => ({
  latestResult: null,
  history: [],
  isLoading: false,
  error: null,
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error, isLoading: false }),
  addResult: (result) =>
    set((state) => ({
      latestResult: result,
      history: [result, ...state.history].slice(0, 25),
      isLoading: false,
      error: null,
    })),
  selectResult: (result) => set({ latestResult: result, error: null }),
  clearResults: () => set({ latestResult: null, history: [], error: null }),
}));
