'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRightIcon, HomeIcon } from '@heroicons/react/24/outline';
import { useLanguage } from '@/lib/contexts/LanguageContext';

export function Breadcrumbs() {
  const pathname = usePathname();
  const { t } = useLanguage();

  const pathNames: Record<string, string> = {
    dashboard: t.breadcrumbs.dashboard,
    'telegram-accounts': t.breadcrumbs.telegramAccounts,
    sources: t.breadcrumbs.sources,
    rules: t.breadcrumbs.rules,
    leads: t.breadcrumbs.leads,
    analytics: t.breadcrumbs.analytics,
    settings: t.breadcrumbs.settings,
    profile: t.breadcrumbs.profile,
  };

  const segments = pathname.split('/').filter(Boolean);

  // Don't show breadcrumbs on dashboard home
  if (segments.length <= 1) {
    return null;
  }

  const breadcrumbs = segments.map((segment, index) => {
    const path = '/' + segments.slice(0, index + 1).join('/');
    const name = pathNames[segment] || segment;
    const isLast = index === segments.length - 1;

    return { path, name, isLast };
  });

  return (
    <nav className="flex items-center gap-2 text-sm mb-6" aria-label="Breadcrumb">
      <Link
        href="/dashboard"
        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
        aria-label="Home"
      >
        <HomeIcon className="w-4 h-4" />
      </Link>

      {breadcrumbs.map(({ path, name, isLast }) => (
        <div key={path} className="flex items-center gap-2">
          <ChevronRightIcon className="w-4 h-4 text-gray-400 dark:text-gray-600" />
          {isLast ? (
            <span className="font-medium text-gray-900 dark:text-white">
              {name}
            </span>
          ) : (
            <Link
              href={path}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            >
              {name}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
}
