import React from 'react';
import { ShieldAlert, Info, AlertTriangle, CheckCircle, X, Check } from 'lucide-react';

export type Severity = 'INFO' | 'WARNING' | 'CRITICAL' | 'SUCCESS';
export type State = 'UNREAD' | 'READ' | 'DISMISSED' | 'ACKNOWLEDGED';

export interface Notification {
  id: string;
  title: string;
  message: string;
  severity: Severity;
  category: string;
  state: State;
  created_at: string;
}

interface NotificationItemProps {
  notification: Notification;
  onMarkRead: (id: string) => void;
  onDismiss: (id: string) => void;
  onAcknowledge: (id: string) => void;
}

const severityConfig = {
  INFO: { icon: Info, color: 'text-blue-500', bg: 'bg-blue-50' },
  WARNING: { icon: AlertTriangle, color: 'text-yellow-500', bg: 'bg-yellow-50' },
  CRITICAL: { icon: ShieldAlert, color: 'text-red-500', bg: 'bg-red-50' },
  SUCCESS: { icon: CheckCircle, color: 'text-green-500', bg: 'bg-green-50' },
};

export const NotificationItem: React.FC<NotificationItemProps> = ({
  notification,
  onMarkRead,
  onDismiss,
  onAcknowledge,
}) => {
  const config = severityConfig[notification.severity] || severityConfig.INFO;
  const Icon = config.icon;
  const isUnread = notification.state === 'UNREAD';

  return (
    <div className={`p-4 border-b flex items-start gap-3 transition-colors ${isUnread ? 'bg-white' : 'bg-gray-50'}`}>
      <div className={`p-2 rounded-full ${config.bg} ${config.color}`}>
        <Icon size={20} />
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-start mb-1">
          <h4 className={`text-sm font-semibold ${isUnread ? 'text-gray-900' : 'text-gray-600'}`}>
            {notification.title}
          </h4>
          <span className="text-xs text-gray-400">
            {new Date(notification.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <p className={`text-sm mb-2 ${isUnread ? 'text-gray-700' : 'text-gray-500'}`}>
          {notification.message}
        </p>
        <div className="flex gap-2">
          {isUnread && (
            <button 
              onClick={() => onMarkRead(notification.id)}
              className="text-xs text-blue-600 hover:text-blue-800 font-medium"
            >
              Mark Read
            </button>
          )}
          {notification.severity === 'CRITICAL' && notification.state !== 'ACKNOWLEDGED' && (
            <button 
              onClick={() => onAcknowledge(notification.id)}
              className="text-xs flex items-center gap-1 text-red-600 hover:text-red-800 font-medium"
            >
              <Check size={14} /> Acknowledge
            </button>
          )}
          <button 
            onClick={() => onDismiss(notification.id)}
            className="text-xs flex items-center gap-1 text-gray-500 hover:text-gray-700 font-medium ml-auto"
          >
            <X size={14} /> Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
