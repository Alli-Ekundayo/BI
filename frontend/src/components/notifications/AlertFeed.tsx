import React, { useEffect } from 'react';
import { NotificationItem, Notification } from './NotificationItem';
import { useNotificationStore } from '../../store/notificationStore';

export const AlertFeed: React.FC = () => {
  const {
    notifications,
    filter,
    setFilter,
    markRead,
    dismiss,
    acknowledge,
    connectSSE
  } = useNotificationStore();

  useEffect(() => {
    // Only connect once
    connectSSE();
  }, []);

  const handleMarkRead = (id: string) => markRead(id);
  const handleDismiss = (id: string) => dismiss(id);
  const handleAcknowledge = (id: string) => acknowledge(id);
    );
  };

  const filteredNotifications = notifications.filter(n => {
    if (n.state === 'DISMISSED') return false;
    if (filter === 'UNREAD') return n.state === 'UNREAD';
    if (filter === 'CRITICAL') return n.severity === 'CRITICAL';
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-md border overflow-hidden">
      <div className="p-4 border-b flex justify-between items-center bg-gray-50">
        <h3 className="font-semibold text-gray-800">Alert Feed</h3>
        <div className="flex space-x-2">
          {['ALL', 'UNREAD', 'CRITICAL'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f as any)}
              className={`text-xs px-2 py-1 rounded-md transition-colors ${
                filter === f 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-white text-gray-600 hover:bg-gray-200 border'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {filteredNotifications.length === 0 ? (
          <div className="p-8 text-center text-gray-400">
            No alerts to display.
          </div>
        ) : (
          filteredNotifications.map(notif => (
            <NotificationItem 
              key={notif.id}
              notification={notif}
              onMarkRead={handleMarkRead}
              onDismiss={handleDismiss}
              onAcknowledge={handleAcknowledge}
            />
          ))
        )}
      </div>
    </div>
  );
};
