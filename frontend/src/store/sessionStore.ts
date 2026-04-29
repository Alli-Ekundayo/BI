import { create } from "zustand";
import type { SessionMessage } from "../types";

interface SessionState {
  sessionId: string;
  messages: SessionMessage[];
  setSessionId: (sessionId: string) => void;
  pushMessage: (message: SessionMessage) => void;
  clearSession: () => void;
}

function createSessionId(): string {
  const random = Math.random().toString(36).slice(2, 10);
  return `session-${Date.now()}-${random}`;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: createSessionId(),
  messages: [],
  setSessionId: (sessionId) => set({ sessionId }),
  pushMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearSession: () =>
    set({
      sessionId: createSessionId(),
      messages: [],
    }),
}));
