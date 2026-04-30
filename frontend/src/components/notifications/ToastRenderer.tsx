import React, { useEffect, useState } from 'react';
import { ShieldAlert, X } from 'lucide-react';
import { Notification } from './NotificationItem';

export const ToastRenderer: React.FC = () => {
  const [toasts, setToasts] = useState<Notification[]>([]);
  const [criticalModal, setCriticalModal] = useState<Notification | null>(null);

  // In a real app, this effect would listen to the SSE stream or a Zustand store
  useEffect(() => {
    const handleNewNotification = (event: CustomEvent<Notification>) => {
      const notif = event.detail;
      
      // Escalation Logic: Critical alerts go straight to modal
      if (notif.severity === 'CRITICAL') {
        setCriticalModal(notif);
      } else {
        setToasts(prev => [...prev, notif]);
        // Auto-dismiss non-critical toasts after 5 seconds
        setTimeout(() => {
          setToasts(prev => prev.filter(t => t.id !== notif.id));
        }, 5000);
      }
    };

    window.addEventListener('new-notification', handleNewNotification as EventListener);
    return () => window.removeEventListener('new-notification', handleNewNotification as EventListener);
  }, []);

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  const handleAcknowledgeModal = () => {
    if (criticalModal) {
      // In a real app, call the API to acknowledge
      console.log('Acknowledged:', criticalModal.id);
      setCriticalModal(null);
    }
  };

  return (
    <>
      {/* Toast Container (Bottom Right) */}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map(toast => (
          <div 
            key={toast.id} 
            className="bg-white border-l-4 border-blue-500 shadow-lg rounded-r-md p-4 w-80 flex items-start justify-between animate-slide-in-right"
          >
            <div>
              <h4 className="text-sm font-bold text-gray-800">{toast.title}</h4>
              <p className="text-xs text-gray-600 mt-1">{toast.message}</p>
            </div>
            <button onClick={() => removeToast(toast.id)} className="text-gray-400 hover:text-gray-600">
              <X size={16} />
            </button>
          </div>
        ))}
      </div>

      {/* Critical Alert Modal Overlay */}
      {criticalModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-[100] flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-lg shadow-2xl max-w-md w-full overflow-hidden">
            <div className="bg-red-500 p-4 flex items-center justify-center text-white">
              <ShieldAlert size={48} />
            </div>
            <div className="p-6 text-center">
              <h2 className="text-xl font-bold text-gray-900 mb-2">Critical Alert: {criticalModal.title}</h2>
              <p className="text-gray-700 mb-6">{criticalModal.message}</p>
              <button 
                onClick={handleAcknowledgeModal}
                className="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-4 rounded transition-colors"
              >
                Acknowledge Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
