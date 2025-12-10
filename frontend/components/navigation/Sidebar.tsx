'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  HomeIcon,
  UserGroupIcon,
  SignalIcon,
  AdjustmentsHorizontalIcon,
  StarIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils/cn';
import { ThemeToggle } from '@/components/theme/ThemeToggle';
import { UserProfileMenu } from '@/components/user/UserProfileMenu';
import { LanguageToggle } from '@/components/language/LanguageToggle';
import { useLanguage } from '@/lib/contexts/LanguageContext';

interface MenuItem {
  key: keyof typeof import('@/lib/i18n/translations').translations.en.nav;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { t } = useLanguage();

  const menuItems: MenuItem[] = [
    {
      key: 'dashboard',
      href: '/dashboard',
      icon: HomeIcon,
    },
    {
      key: 'telegramAccounts',
      href: '/dashboard/telegram-accounts',
      icon: UserGroupIcon,
    },
    {
      key: 'sources',
      href: '/dashboard/subscriptions',
      icon: SignalIcon,
    },
    {
      key: 'rules',
      href: '/dashboard/rules',
      icon: AdjustmentsHorizontalIcon,
    },
    {
      key: 'leads',
      href: '/dashboard/leads',
      icon: StarIcon,
    },
    {
      key: 'analytics',
      href: '/dashboard/analytics',
      icon: ChartBarIcon,
    },
    {
      key: 'settings',
      href: '/dashboard/settings',
      icon: Cog6ToothIcon,
    },
  ];

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard';
    }
    return pathname.startsWith(href);
  };

  const sidebarContent = (
    <div className="flex h-full flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="px-4 py-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-xl">T</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">
                Telegram Lead Monitor
              </h1>
              <p className="text-xs text-gray-500 dark:text-gray-400">v0.1.0</p>
            </div>
          </div>

          {/* Close button - only visible on mobile */}
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            aria-label="Close sidebar"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => {
                // Close mobile sidebar when clicking a link
                if (window.innerWidth < 1024) {
                  onClose();
                }
              }}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                active
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
              )}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span className="font-medium">{t.nav[item.key]}</span>
              {item.badge && (
                <span className="ml-auto bg-primary-600 text-white text-xs px-2 py-0.5 rounded-full">
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer - user profile, language and theme toggle */}
      <div className="px-4 py-4 border-t border-gray-200 dark:border-gray-700 space-y-2">
        <UserProfileMenu />
        <div className="grid grid-cols-2 gap-2">
          <LanguageToggle />
          <ThemeToggle />
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar - always visible on lg+ screens */}
      <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        {sidebarContent}
      </aside>

      {/* Mobile sidebar - overlay */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-gray-900/80 z-40 lg:hidden"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Sidebar */}
          <aside
            className={cn(
              'fixed inset-y-0 left-0 w-64 z-50 lg:hidden',
              'transform transition-transform duration-300 ease-in-out',
              isOpen ? 'translate-x-0' : '-translate-x-full'
            )}
          >
            {sidebarContent}
          </aside>
        </>
      )}
    </>
  );
}
