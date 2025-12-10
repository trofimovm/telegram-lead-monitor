'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { notificationsApi } from '@/lib/api/notifications';
import { NotificationPreferences } from '@/lib/api/notification-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';
import TelegramBotConnection from '@/components/settings/TelegramBotConnection';

export default function SettingsPage() {
  const { t } = useLanguage();
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    email_notifications_enabled: true,
    in_app_notifications_enabled: true,
    telegram_bot_enabled: false,
    notify_on_new_lead: true,
    notify_on_lead_status_change: false,
    notify_on_lead_assignment: true,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savingField, setSavingField] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      const data = await notificationsApi.getPreferences();
      setPreferences(data);
    } catch (error) {
      console.error('Failed to load preferences:', error);
      setSaveMessage({ type: 'error', text: t.settings.failedToLoad });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setSaveMessage(null);

      await notificationsApi.updatePreferences(preferences);

      setSaveMessage({ type: 'success', text: t.settings.settingsSaved });

      // Скрыть сообщение через 3 секунды
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      console.error('Failed to save preferences:', error);
      setSaveMessage({ type: 'error', text: t.settings.failedToSave });
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (field: keyof NotificationPreferences) => {
    // Optimistic UI update
    const newValue = !preferences[field];
    setPreferences((prev) => ({
      ...prev,
      [field]: newValue,
    }));

    // Auto-save immediately
    try {
      setSavingField(field);
      setSaveMessage(null);

      await notificationsApi.updatePreferences({
        ...preferences,
        [field]: newValue,
      });

      // Show brief success message
      setSaveMessage({ type: 'success', text: t.settings.settingsSaved });
      setTimeout(() => setSaveMessage(null), 2000);
    } catch (error) {
      // Revert on error
      setPreferences((prev) => ({
        ...prev,
        [field]: !newValue,
      }));
      console.error('Failed to save preference:', error);
      setSaveMessage({ type: 'error', text: t.settings.failedToSave });
    } finally {
      setSavingField(null);
    }
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">{t.settings.title}</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {t.settings.subtitle}
            </p>
          </div>

          {/* Notification Preferences Card */}
          <Card>
            <CardHeader>
              <CardTitle>{t.settings.notificationSettings}</CardTitle>
              <CardDescription>
                {t.settings.notificationSettingsDesc}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8">
                  <p className="text-gray-500">{t.settings.loadingSettings}</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Global Toggles */}
                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {t.settings.emailNotifications}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {t.settings.emailNotificationsDesc}
                        </p>
                      </div>
                      <button
                        onClick={() => handleToggle('email_notifications_enabled')}
                        disabled={savingField === 'email_notifications_enabled'}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          preferences.email_notifications_enabled ? 'bg-primary-600' : 'bg-gray-300'
                        } ${savingField === 'email_notifications_enabled' ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            preferences.email_notifications_enabled ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {savingField === 'email_notifications_enabled' && (
                          <span className="absolute inset-0 flex items-center justify-center">
                            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          </span>
                        )}
                      </button>
                    </div>

                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {t.settings.inAppNotifications}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {t.settings.inAppNotificationsDesc}
                        </p>
                      </div>
                      <button
                        onClick={() => handleToggle('in_app_notifications_enabled')}
                        disabled={savingField === 'in_app_notifications_enabled'}
                        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                          preferences.in_app_notifications_enabled ? 'bg-primary-600' : 'bg-gray-300'
                        } ${savingField === 'in_app_notifications_enabled' ? 'opacity-50 cursor-not-allowed' : ''}`}
                      >
                        <span
                          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                            preferences.in_app_notifications_enabled ? 'translate-x-6' : 'translate-x-1'
                          }`}
                        />
                        {savingField === 'in_app_notifications_enabled' && (
                          <span className="absolute inset-0 flex items-center justify-center">
                            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          </span>
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Telegram Notifications Section */}
                  <div className="space-y-4 pb-6 border-b border-gray-200">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                        Telegram Notifications
                      </h3>

                      <TelegramBotConnection
                        onConnectionChange={(connected) => {
                          if (!connected) {
                            setPreferences((prev) => ({ ...prev, telegram_bot_enabled: false }));
                          }
                        }}
                      />

                      {/* Enable/Disable Toggle */}
                      <div className="flex items-start justify-between mt-4 pt-4 border-t border-gray-100">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            Enable Telegram Notifications
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Send notifications to Telegram when enabled
                          </p>
                        </div>
                        <button
                          onClick={() => handleToggle('telegram_bot_enabled')}
                          disabled={savingField === 'telegram_bot_enabled'}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            preferences.telegram_bot_enabled ? 'bg-primary-600' : 'bg-gray-300'
                          } ${savingField === 'telegram_bot_enabled' ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              preferences.telegram_bot_enabled ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                          {savingField === 'telegram_bot_enabled' && (
                            <span className="absolute inset-0 flex items-center justify-center">
                              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            </span>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Event Types */}
                  <div className="space-y-4">
                    <h3 className="text-md font-medium text-gray-900 dark:text-white">
                      {t.settings.eventTypes}
                    </h3>

                    <div className="space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            {t.settings.newLeads}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {t.settings.newLeadsDesc}
                          </p>
                        </div>
                        <button
                          onClick={() => handleToggle('notify_on_new_lead')}
                          disabled={savingField === 'notify_on_new_lead'}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            preferences.notify_on_new_lead ? 'bg-primary-600' : 'bg-gray-300'
                          } ${savingField === 'notify_on_new_lead' ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              preferences.notify_on_new_lead ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                          {savingField === 'notify_on_new_lead' && (
                            <span className="absolute inset-0 flex items-center justify-center">
                              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            </span>
                          )}
                        </button>
                      </div>

                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            {t.settings.leadStatusChange}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {t.settings.leadStatusChangeDesc}
                          </p>
                        </div>
                        <button
                          onClick={() => handleToggle('notify_on_lead_status_change')}
                          disabled={savingField === 'notify_on_lead_status_change'}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            preferences.notify_on_lead_status_change ? 'bg-primary-600' : 'bg-gray-300'
                          } ${savingField === 'notify_on_lead_status_change' ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              preferences.notify_on_lead_status_change ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                          {savingField === 'notify_on_lead_status_change' && (
                            <span className="absolute inset-0 flex items-center justify-center">
                              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            </span>
                          )}
                        </button>
                      </div>

                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                            {t.settings.leadAssignment}
                          </h4>
                          <p className="text-sm text-gray-600 mt-1">
                            {t.settings.leadAssignmentDesc}
                          </p>
                        </div>
                        <button
                          onClick={() => handleToggle('notify_on_lead_assignment')}
                          disabled={savingField === 'notify_on_lead_assignment'}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            preferences.notify_on_lead_assignment ? 'bg-primary-600' : 'bg-gray-300'
                          } ${savingField === 'notify_on_lead_assignment' ? 'opacity-50 cursor-not-allowed' : ''}`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              preferences.notify_on_lead_assignment ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                          {savingField === 'notify_on_lead_assignment' && (
                            <span className="absolute inset-0 flex items-center justify-center">
                              <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                            </span>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Save Button */}
                  <div className="flex items-center gap-4 pt-6 border-t border-gray-200">
                    <Button onClick={handleSave} disabled={saving}>
                      {saving ? t.settings.saving : t.settings.saveSettings}
                    </Button>

                    {saveMessage && (
                      <p
                        className={`text-sm ${
                          saveMessage.type === 'success' ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {saveMessage.text}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
