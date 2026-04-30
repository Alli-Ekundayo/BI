import { create } from 'zustand';
import { Notification } from '../components/notifications/NotificationItem';

interface NotificationState {
  notifications: Notification[];
  filter: 'ALL' | 'UNREAD' | 'CRITICAL';
  setFilter: (filter: 'ALL' | 'UNREAD' | 'CRITICAL') => void;
  markRead: (id: string) => void;
  dismiss: (id: string) => void;
  acknowledge: (id: string) => void;
  addNotification: (notification: Notification) => void;
  connectSSE: () => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  filter: 'ALL',
  setFilter: (filter) => set({ filter }),
  markRead: (id) => set((state) => ({
    notifications: state.notifications.map(n => n.id === id ? { ...n, state: 'READ' } : n)
  })),
  dismiss: (id) => set((state) => ({
    notifications: state.notifications.map(n => n.id === id ? { ...n, state: 'DISMISSED' } : n)
  })),
  acknowledge: (id) => set((state) => ({
    notifications: state.notifications.map(n => n.id === id ? { ...n, state: 'ACKNOWLEDGED' } : n)
  })),
  addNotification: (notification) => set((state) => ({
    notifications: [notification, ...state.notifications]
  })),
  connectSSE: () => {
    // Determine backend URL, assuming Vite's env or defaulting to localhost
    const baseUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";
    const eventSource = new EventSource(`${baseUrl}/notifications/stream`);
    
    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'notification' && payload.data) {
          get().addNotification(payload.data);
          
          // Dispatch custom event for ToastRenderer
          window.dispatchEvent(new CustomEvent('new-notification', { detail: payload.data }));
        }
      } catch (err) {
        console.error("Failed to parse SSE message", err);
      }
    };
    
    eventSource.onerror = (err) => {
      console.error("SSE connection error", err);
    };
  }
}));
