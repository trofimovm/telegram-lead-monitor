'use client';

import { useRouter } from 'next/navigation';
import { Bars3Icon } from '@heroicons/react/24/outline';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Button } from '@/components/ui/Button';
import { NotificationBell } from '@/components/notifications/NotificationBell';

interface MobileHeaderProps {
  onMenuClick: () => void;
}

export function MobileHeader({ onMenuClick }: MobileHeaderProps) {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  return (
    <header className="lg:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm sticky top-0 z-30">
      <div className="px-4 sm:px-6">
        <div className="flex justify-between items-center h-16">
          {/* Left: Menu button and Logo */}
          <div className="flex items-center gap-3">
            <button
              onClick={onMenuClick}
              className="p-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              aria-label="Open menu"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>

            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white hidden sm:block">
                TLM
              </h1>
            </div>
          </div>

          {/* Right: Notifications and User */}
          <div className="flex items-center gap-2">
            {/* Notification Bell */}
            <NotificationBell />

            {/* User info - hidden on very small screens */}
            <div className="hidden sm:flex items-center gap-2">
              <div className="text-sm text-right">
                <p className="text-gray-900 dark:text-white font-medium">
                  {user?.full_name}
                </p>
                <p className="text-gray-500 dark:text-gray-400 text-xs">
                  {user?.email}
                </p>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Sign Out
              </Button>
            </div>

            {/* Mobile: Just sign out button */}
            <div className="sm:hidden">
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Out
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
