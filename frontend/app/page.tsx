'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/contexts/AuthContext';
import { Button } from '@/components/ui/Button';

export default function Home() {
  const { user, loading } = useAuth();
  const router = useRouter();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (!loading && user) {
      router.push('/dashboard');
    }
  }, [user, loading, router]);

  // Show loading spinner while checking auth
  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white dark:bg-gray-900">
        <svg className="animate-spin h-12 w-12 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </main>
    );
  }

  // If authenticated, don't render (will redirect)
  if (user) {
    return null;
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-white dark:bg-gray-900">
      {/* Header with Sign In link */}
      <div className="absolute top-8 right-8">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Already have an account?{' '}
          <Link
            href="/login"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Sign In
          </Link>
        </p>
      </div>

      <div className="z-10 w-full max-w-5xl items-center justify-center font-mono text-sm">
        <h1 className="text-5xl font-bold mb-4 text-gray-900 dark:text-gray-100 text-center">
          <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
            Telegram Lead Monitor
          </span>
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 text-center mb-8">
          Monitor Telegram channels and find relevant leads with AI analysis
        </p>

        <div className="flex justify-center gap-4">
          {/* Primary CTA: Get Started → Register */}
          <Button
            variant="primary"
            size="lg"
            onClick={() => router.push('/register')}
            className="hover:shadow-xl transition-all duration-300 hover:scale-105"
          >
            Get Started
          </Button>

          {/* Secondary CTA: Sign In */}
          <Button
            variant="outline"
            size="lg"
            onClick={() => router.push('/login')}
            className="hover:shadow-lg transition-all duration-300"
          >
            Sign In
          </Button>
        </div>

        {/* Optional: Feature highlights */}
        <div className="mt-12 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>No credit card required • Free tier available • Cancel anytime</p>
        </div>
      </div>
    </main>
  );
}
