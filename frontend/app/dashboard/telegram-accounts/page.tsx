'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { telegramApi } from '@/lib/api/telegram';
import { TelegramAccountResponse, StartAuthResponse } from '@/lib/api/telegram-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';

export default function TelegramAccountsPage() {
  const { t } = useLanguage();
  const [accounts, setAccounts] = useState<TelegramAccountResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add account modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [addStep, setAddStep] = useState<'phone' | 'code'>('phone');
  const [phone, setPhone] = useState('');
  const [code, setCode] = useState('');
  const [phoneCodeHash, setPhoneCodeHash] = useState('');
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const data = await telegramApi.listAccounts();
      setAccounts(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || t.telegramAccounts.failedToLoad);
    } finally {
      setLoading(false);
    }
  };

  const handleStartAuth = async () => {
    if (!phone) {
      setAddError(t.telegramAccounts.enterPhone);
      return;
    }

    try {
      setAddLoading(true);
      setAddError(null);
      const result = await telegramApi.startAuth({ phone });
      setPhoneCodeHash(result.phone_code_hash);
      setAddStep('code');
    } catch (err: any) {
      setAddError(err.response?.data?.detail || t.telegramAccounts.failedToSendCode);
    } finally {
      setAddLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!code) {
      setAddError(t.telegramAccounts.enterCode);
      return;
    }

    try {
      setAddLoading(true);
      setAddError(null);
      await telegramApi.verifyCode({ phone, code, phone_code_hash: phoneCodeHash });

      // Success - reload accounts and close modal
      await loadAccounts();
      setShowAddModal(false);
      resetAddModal();
    } catch (err: any) {
      setAddError(err.response?.data?.detail || t.telegramAccounts.failedToVerify);
    } finally {
      setAddLoading(false);
    }
  };

  const handleDeleteAccount = async (accountId: string) => {
    if (!confirm(t.telegramAccounts.confirmDisconnect)) {
      return;
    }

    try {
      await telegramApi.deleteAccount(accountId);
      await loadAccounts();
    } catch (err: any) {
      alert(err.response?.data?.detail || t.telegramAccounts.failedToDelete);
    }
  };

  const resetAddModal = () => {
    setPhone('');
    setCode('');
    setPhoneCodeHash('');
    setAddStep('phone');
    setAddError(null);
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">{t.telegramAccounts.title}</h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                {t.telegramAccounts.subtitle}
              </p>
            </div>
            <Button onClick={() => setShowAddModal(true)}>
              {t.telegramAccounts.addAccount}
            </Button>
          </div>

          {error && (
            <Alert variant="error">{error}</Alert>
          )}

          {loading ? (
            <div className="flex justify-center py-12">
              <svg className="animate-spin h-12 w-12 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          ) : accounts.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">{t.telegramAccounts.noAccounts}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">{t.telegramAccounts.noAccountsDesc}</p>
                <Button onClick={() => setShowAddModal(true)}>
                  {t.telegramAccounts.addFirstAccount}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {accounts.map((account) => (
                <Card key={account.id}>
                  <CardHeader>
                    <CardTitle className="text-lg">{account.phone}</CardTitle>
                    <CardDescription>
                      {t.telegramAccounts.status}: <span className={`font-medium ${account.status === 'active' ? 'text-green-600' : 'text-gray-600 dark:text-gray-400'}`}>
                        {account.status}
                      </span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                      <div>
                        <strong>{t.telegramAccounts.connected}:</strong> {new Date(account.created_at).toLocaleDateString()}
                      </div>
                      {account.last_active_at && (
                        <div>
                          <strong>{t.telegramAccounts.lastActive}:</strong> {new Date(account.last_active_at).toLocaleDateString()}
                        </div>
                      )}
                    </div>
                    <div className="mt-4 flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => window.location.href = `/dashboard/sources?account=${account.id}`}
                      >
                        {t.telegramAccounts.viewSources}
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteAccount(account.id)}
                      >
                        {t.telegramAccounts.disconnect}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Add Account Modal */}
          {showAddModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <Card className="w-full max-w-md">
                <CardHeader>
                  <CardTitle>{t.telegramAccounts.addAccountModal}</CardTitle>
                  <CardDescription>
                    {addStep === 'phone'
                      ? t.telegramAccounts.enterPhoneDesc
                      : t.telegramAccounts.enterCodeDesc}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {addError && (
                    <Alert variant="error">{addError}</Alert>
                  )}

                  {addStep === 'phone' ? (
                    <>
                      <Input
                        label={t.telegramAccounts.phoneNumber}
                        type="tel"
                        placeholder="+1234567890"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        disabled={addLoading}
                      />
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          onClick={() => {
                            setShowAddModal(false);
                            resetAddModal();
                          }}
                          disabled={addLoading}
                          className="flex-1"
                        >
                          {t.common.cancel}
                        </Button>
                        <Button
                          onClick={handleStartAuth}
                          loading={addLoading}
                          className="flex-1"
                        >
                          {t.telegramAccounts.sendCode}
                        </Button>
                      </div>
                    </>
                  ) : (
                    <>
                      <Alert variant="info">
                        {t.telegramAccounts.codeSentTo.replace('{{phone}}', phone)}
                      </Alert>
                      <Input
                        label={t.telegramAccounts.verificationCode}
                        type="text"
                        placeholder="12345"
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                        disabled={addLoading}
                        autoFocus
                      />
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          onClick={() => {
                            setShowAddModal(false);
                            resetAddModal();
                          }}
                          disabled={addLoading}
                          className="flex-1"
                        >
                          {t.common.cancel}
                        </Button>
                        <Button
                          onClick={handleVerifyCode}
                          loading={addLoading}
                          className="flex-1"
                        >
                          {t.telegramAccounts.verify}
                        </Button>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
