'use client';

import { useState } from 'react';
import { Sidebar } from '@/components/navigation/Sidebar';
import { MobileHeader } from '@/components/navigation/MobileHeader';
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Sidebar - fixed on desktop, overlay on mobile */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Mobile header - visible only on mobile/tablet */}
      <MobileHeader onMenuClick={() => setSidebarOpen(true)} />

      {/* Main content - with left padding on desktop to account for sidebar */}
      <div className="lg:pl-64">
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Breadcrumbs />
          {children}
        </main>
      </div>
    </div>
  );
}
