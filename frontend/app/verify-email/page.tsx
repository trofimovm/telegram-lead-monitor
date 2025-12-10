'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { authApi } from '@/lib/api/auth';
import { Button } from '@/components/ui/Button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Alert } from '@/components/ui/Alert';

function VerifyEmailContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setMessage('Invalid verification link. No token provided.');
      return;
    }

    verifyEmail(token);
  }, [token]);

  const verifyEmail = async (token: string) => {
    try {
      const response = await authApi.verifyEmail({ token });
      setStatus('success');
      setMessage(response.message || 'Email verified successfully!');
    } catch (err: any) {
      setStatus('error');
      setMessage(err.response?.data?.detail || 'Email verification failed. The link may be invalid or expired.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100 p-4">
      <div className="w-full max-w-md">
        <Card>
          <CardHeader>
            <CardTitle className="text-center">Email Verification</CardTitle>
            <CardDescription className="text-center">
              Verifying your email address
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            {status === 'loading' && (
              <div className="flex flex-col items-center justify-center py-8">
                <svg
                  className="animate-spin h-12 w-12 text-primary-600 mb-4"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <p className="text-gray-600">Verifying your email...</p>
              </div>
            )}

            {status === 'success' && (
              <>
                <Alert variant="success">
                  {message}
                </Alert>
                <div className="flex flex-col items-center justify-center py-4">
                  <svg
                    className="h-16 w-16 text-green-500 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-gray-600 text-center mb-4">
                    Your email has been verified. You can now sign in to your account.
                  </p>
                  <Button
                    variant="primary"
                    onClick={() => router.push('/login')}
                  >
                    Go to Login
                  </Button>
                </div>
              </>
            )}

            {status === 'error' && (
              <>
                <Alert variant="error">
                  {message}
                </Alert>
                <div className="flex flex-col items-center justify-center py-4">
                  <svg
                    className="h-16 w-16 text-red-500 mb-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-gray-600 text-center mb-4">
                    Need a new verification link?
                  </p>
                  <Link href="/resend-verification">
                    <Button variant="outline">
                      Resend Verification Email
                    </Button>
                  </Link>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin h-12 w-12 text-primary-600" />
      </div>
    }>
      <VerifyEmailContent />
    </Suspense>
  );
}
