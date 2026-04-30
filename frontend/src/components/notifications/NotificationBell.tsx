import React, { useState, useRef, useEffect } from 'react';
import { Bell } from 'lucide-react';
import { AlertFeed } from './AlertFeed';

export const NotificationBell: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  // Mocking unread count. In reality, it comes from global state connected to SSE.
  const [unreadCount] = useState(3); 
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-full hover:bg-gray-100 relative transition-colors focus:outline-none"
      >
        <Bell size={24} className="text-gray-600" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white ring-2 ring-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-96 max-h-[80vh] bg-white rounded-lg shadow-xl border overflow-hidden z-50">
          <AlertFeed />
        </div>
      )}
    </div>
  );
};
