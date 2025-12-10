'use client';

import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/contexts/AuthContext';
import { useLanguage } from '@/lib/contexts/LanguageContext';
import {
  UserCircleIcon,
  ChevronUpDownIcon,
  PencilSquareIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils/cn';

export function UserProfileMenu() {
  const { user, logout } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const handleEditProfile = () => {
    router.push('/dashboard/profile');
  };

  if (!user) return null;

  return (
    <Menu as="div" className="relative">
      <Menu.Button className="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
        <div className="flex items-center gap-2 min-w-0">
          <UserCircleIcon className="w-5 h-5 flex-shrink-0" />
          <div className="flex-1 text-left overflow-hidden">
            <p className="font-medium truncate">{user.full_name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
          </div>
        </div>
        <ChevronUpDownIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
      </Menu.Button>

      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items className="absolute bottom-full left-0 right-0 mb-2 bg-white dark:bg-gray-700 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 py-1 focus:outline-none z-10">
          <Menu.Item>
            {({ active }) => (
              <button
                onClick={handleEditProfile}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-700 dark:text-gray-300',
                  active && 'bg-gray-100 dark:bg-gray-600'
                )}
              >
                <PencilSquareIcon className="w-4 h-4" />
                <span>{t.user.editProfile}</span>
              </button>
            )}
          </Menu.Item>

          <div className="border-t border-gray-200 dark:border-gray-600 my-1" />

          <Menu.Item>
            {({ active }) => (
              <button
                onClick={handleLogout}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 text-sm text-red-600 dark:text-red-400',
                  active && 'bg-gray-100 dark:bg-gray-600'
                )}
              >
                <ArrowRightOnRectangleIcon className="w-4 h-4" />
                <span>{t.user.signOut}</span>
              </button>
            )}
          </Menu.Item>
        </Menu.Items>
      </Transition>
    </Menu>
  );
}
