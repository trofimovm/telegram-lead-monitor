'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { telegramApi } from '@/lib/api/telegram';
import {
  SubscriptionResponse,
  TelegramAccountResponse,
  DialogInfo
} from '@/lib/api/telegram-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';

export default function SubscriptionsPage() {
  const { t } = useLanguage();
  const [subscriptions, setSubscriptions] = useState<SubscriptionResponse[]>([]);
  const [accounts, setAccounts] = useState<TelegramAccountResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add subscription modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  const [dialogs, setDialogs] = useState<DialogInfo[]>([]);
  const [loadingDialogs, setLoadingDialogs] = useState(false);
  const [selectedDialog, setSelectedDialog] = useState<DialogInfo | null>(null);
  const [addLoading, setAddLoading] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [subscriptionsData, accountsData] = await Promise.all([
        telegramApi.listSubscriptions(),
        telegramApi.listAccounts(),
      ]);
      setSubscriptions(subscriptionsData);
      setAccounts(accountsData);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load subscriptions');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadDialogs = async (accountId: string) => {
    setSelectedAccount(accountId);
    setLoadingDialogs(true);
    setAddError(null);

    try {
      const dialogsData = await telegramApi.getDialogs(accountId);
      // Filter only channels and groups
      const filtered = dialogsData.filter(d => d.is_channel || d.is_group);
      setDialogs(filtered);
    } catch (err: any) {
      setAddError(err.response?.data?.detail || 'Failed to load channels');
    } finally {
      setLoadingDialogs(false);
    }
  };

  const handleAddSubscription = async () => {
    if (!selectedDialog) {
      setAddError('Please select a channel');
      return;
    }

    try {
      setAddLoading(true);
      setAddError(null);

      await telegramApi.createSubscription({
        telegram_account_id: selectedAccount,
        tg_id: selectedDialog.id,
        username: selectedDialog.username || undefined,
        title: selectedDialog.title,
        channel_type: selectedDialog.is_channel ? 'channel' : selectedDialog.is_group ? 'group' : 'chat',
        tags: [],
      });

      await loadData();
      setShowAddModal(false);
      resetAddModal();
    } catch (err: any) {
      setAddError(err.response?.data?.detail || 'Failed to add subscription');
    } finally {
      setAddLoading(false);
    }
  };

  const handleToggleActive = async (subscriptionId: string, currentActive: boolean) => {
    try {
      await telegramApi.updateSubscription(subscriptionId, { is_active: !currentActive });
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update subscription');
    }
  };

  const handleDeleteSubscription = async (subscriptionId: string) => {
    if (!confirm('Are you sure you want to delete this subscription?')) {
      return;
    }

    try {
      await telegramApi.deleteSubscription(subscriptionId);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete subscription');
    }
  };

  const resetAddModal = () => {
    setSelectedAccount('');
    setDialogs([]);
    setSelectedDialog(null);
    setAddError(null);
  };

  const openAddModal = () => {
    if (accounts.length === 0) {
      alert('Please connect a Telegram account first');
      return;
    }
    setShowAddModal(true);
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Channel Subscriptions</h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                Manage channels and groups you monitor for leads
              </p>
            </div>
            <Button onClick={openAddModal}>
              Add Subscription
            </Button>
          </div>

          {error && <Alert variant="error">{error}</Alert>}

          {loading ? (
            <div className="flex justify-center py-12">
              <svg className="animate-spin h-12 w-12 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          ) : subscriptions.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No subscriptions yet</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">Add channels and groups to start monitoring for leads</p>
                <Button onClick={openAddModal}>
                  Add First Subscription
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {subscriptions.map((subscription) => (
                <Card key={subscription.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-lg truncate">
                          {subscription.channel_title || subscription.channel_username || 'Unnamed Channel'}
                        </CardTitle>
                        <CardDescription className="truncate">
                          {subscription.channel_username && `@${subscription.channel_username}`}
                        </CardDescription>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        subscription.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {subscription.is_active ? 'Active' : 'Paused'}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400 mb-4">
                      <div>
                        <strong>Type:</strong> {subscription.channel_type}
                      </div>
                      <div>
                        <strong>Added:</strong> {new Date(subscription.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => handleToggleActive(subscription.id, subscription.is_active)}
                      >
                        {subscription.is_active ? 'Pause' : 'Activate'}
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteSubscription(subscription.id)}
                      >
                        Remove
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Add Subscription Modal */}
          {showAddModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <Card className="w-full max-w-2xl max-h-[80vh] overflow-hidden flex flex-col">
                <div className="overflow-y-auto">
                  <CardHeader>
                    <CardTitle>Add Channel Subscription</CardTitle>
                    <CardDescription>
                      Select a Telegram account and channel to monitor
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                  {addError && <Alert variant="error">{addError}</Alert>}

                  {/* Step 1: Select Account */}
                  {!selectedAccount && (
                    <div className="space-y-4">
                      <h3 className="font-medium text-gray-900 dark:text-white">Select Telegram Account</h3>
                      <div className="space-y-2">
                        {accounts.map((account) => (
                          <button
                            key={account.id}
                            onClick={() => handleLoadDialogs(account.id)}
                            className="w-full p-4 text-left border border-gray-300 dark:border-gray-600 rounded-lg hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                          >
                            <div className="font-medium text-gray-900 dark:text-white">{account.phone}</div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">{account.status}</div>
                          </button>
                        ))}
                      </div>
                      <Button
                        variant="outline"
                        onClick={() => setShowAddModal(false)}
                        className="w-full"
                      >
                        Cancel
                      </Button>
                    </div>
                  )}

                  {/* Step 2: Select Channel */}
                  {selectedAccount && (
                    <div className="space-y-4">
                      <h3 className="font-medium text-gray-900 dark:text-white">Select Channel or Group</h3>

                      {loadingDialogs ? (
                        <div className="flex justify-center py-8">
                          <svg className="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                        </div>
                      ) : dialogs.length === 0 ? (
                        <div className="text-center py-8 text-gray-600 dark:text-gray-400">
                          No channels found
                        </div>
                      ) : (
                        <div className="space-y-2 max-h-96 overflow-y-auto">
                          {dialogs.map((dialog) => (
                            <button
                              key={dialog.id}
                              onClick={() => setSelectedDialog(dialog)}
                              className={`w-full p-4 text-left border rounded-lg transition-colors ${
                                selectedDialog?.id === dialog.id
                                  ? 'border-primary-500 dark:border-primary-400 bg-primary-50 dark:bg-primary-900/30'
                                  : 'border-gray-300 dark:border-gray-600 hover:border-primary-500 dark:hover:border-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                  <div className="font-medium text-gray-900 dark:text-white truncate">{dialog.title}</div>
                                  {dialog.username && (
                                    <div className="text-sm text-gray-600 dark:text-gray-400 truncate">@{dialog.username}</div>
                                  )}
                                </div>
                                <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 px-2 py-1 rounded">
                                  {dialog.is_channel ? 'Channel' : 'Group'}
                                </span>
                              </div>
                              {dialog.participants_count && (
                                <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                  {dialog.participants_count.toLocaleString()} members
                                </div>
                              )}
                            </button>
                          ))}
                        </div>
                      )}

                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          onClick={() => {
                            setShowAddModal(false);
                            resetAddModal();
                          }}
                          className="flex-1"
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={handleAddSubscription}
                          loading={addLoading}
                          disabled={!selectedDialog}
                          className="flex-1"
                        >
                          Add Subscription
                        </Button>
                      </div>
                    </div>
                  )}
                </CardContent>
                </div>
              </Card>
            </div>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
