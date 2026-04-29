import { useSessionStore } from "../store/sessionStore";

export function useSession() {
  const { sessionId, messages, clearSession } = useSessionStore();
  return { sessionId, messages, clearSession };
}
