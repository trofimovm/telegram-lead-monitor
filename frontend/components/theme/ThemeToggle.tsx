'use client';

import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useTheme } from '@/lib/contexts/ThemeContext';
import { SunIcon, MoonIcon, ComputerDesktopIcon, ChevronUpDownIcon, CheckIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils/cn';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const options = [
    { value: 'light' as const, icon: SunIcon, label: 'Light' },
    { value: 'dark' as const, icon: MoonIcon, label: 'Dark' },
    { value: 'system' as const, icon: ComputerDesktopIcon, label: 'System' },
  ];

  const currentOption = options.find(opt => opt.value === theme) || options[0];
  const CurrentIcon = currentOption.icon;

  return (
    <Menu as="div" className="relative">
      <Menu.Button
        className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors"
        aria-label={`Current theme: ${currentOption.label}`}
        title={currentOption.label}
      >
        <CurrentIcon className="w-5 h-5" />
        <ChevronUpDownIcon className="w-4 h-4 text-gray-400" />
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
          {options.map(({ value, icon: Icon, label }) => (
            <Menu.Item key={value}>
              {({ active }) => (
                <button
                  onClick={() => setTheme(value)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2 text-sm',
                    active && 'bg-gray-100 dark:bg-gray-600',
                    theme === value ? 'text-primary-600 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  <span className="flex-1 text-left">{label}</span>
                  {theme === value && <CheckIcon className="w-4 h-4" />}
                </button>
              )}
            </Menu.Item>
          ))}
        </Menu.Items>
      </Transition>
    </Menu>
  );
}
