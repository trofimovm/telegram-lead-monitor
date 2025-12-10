'use client';

import { Fragment } from 'react';
import { Menu, Transition } from '@headlessui/react';
import { useLanguage } from '@/lib/contexts/LanguageContext';
import { Language } from '@/lib/i18n/translations';
import { GlobeAltIcon, ChevronUpDownIcon, CheckIcon } from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils/cn';

export function LanguageToggle() {
  const { language, setLanguage } = useLanguage();

  const languages: { value: Language; label: string; nativeLabel: string }[] = [
    { value: 'en', label: 'English', nativeLabel: 'EN' },
    { value: 'ru', label: 'Русский', nativeLabel: 'RU' },
  ];

  const currentLang = languages.find(lang => lang.value === language) || languages[0];

  return (
    <Menu as="div" className="relative">
      <Menu.Button className="w-full flex items-center justify-between gap-2 px-3 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
        <div className="flex items-center gap-2">
          <GlobeAltIcon className="w-4 h-4" />
          <span>{currentLang.nativeLabel}</span>
        </div>
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
          {languages.map(({ value, label, nativeLabel }) => (
            <Menu.Item key={value}>
              {({ active }) => (
                <button
                  onClick={() => setLanguage(value)}
                  className={cn(
                    'w-full flex items-center gap-3 px-3 py-2 text-sm',
                    active && 'bg-gray-100 dark:bg-gray-600',
                    language === value ? 'text-primary-600 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
                  )}
                >
                  <span className="flex-1 text-left">
                    <span className="font-medium">{nativeLabel}</span>
                    <span className="ml-2 text-gray-500 dark:text-gray-400">({label})</span>
                  </span>
                  {language === value && <CheckIcon className="w-4 h-4" />}
                </button>
              )}
            </Menu.Item>
          ))}
        </Menu.Items>
      </Transition>
    </Menu>
  );
}
