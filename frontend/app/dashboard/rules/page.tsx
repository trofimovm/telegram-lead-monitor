'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Alert } from '@/components/ui/Alert';
import { rulesApi } from '@/lib/api/rules';
import { telegramApi } from '@/lib/api/telegram';
import { RuleResponse, RuleFormData, RuleTestResponse } from '@/lib/api/rule-types';
import { SubscriptionResponse } from '@/lib/api/telegram-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';

export default function RulesPage() {
  const { t } = useLanguage();
  // State для списка правил и подписок
  const [rules, setRules] = useState<RuleResponse[]>([]);
  const [subscriptions, setSubscriptions] = useState<SubscriptionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State для Add/Edit Modal
  const [showFormModal, setShowFormModal] = useState(false);
  const [editingRule, setEditingRule] = useState<RuleResponse | null>(null);
  const [formData, setFormData] = useState<RuleFormData>({
    name: '',
    description: '',
    prompt: '',
    threshold: 0.7,
    channel_ids: [],
    is_active: true,
  });
  const [formLoading, setFormLoading] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // State для Test Modal
  const [showTestModal, setShowTestModal] = useState(false);
  const [testingRule, setTestingRule] = useState<RuleResponse | null>(null);
  const [testMessage, setTestMessage] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState<RuleTestResponse | null>(null);
  const [testError, setTestError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rulesData, subscriptionsData] = await Promise.all([
        rulesApi.listRules(),
        telegramApi.listSubscriptions(),
      ]);
      setRules(rulesData);
      setSubscriptions(subscriptionsData);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || t.rules.failedToLoad);
    } finally {
      setLoading(false);
    }
  };

  const openAddModal = () => {
    setEditingRule(null);
    setFormData({
      name: '',
      description: '',
      prompt: '',
      threshold: 0.7,
      channel_ids: [],
      is_active: true,
    });
    setFormError(null);
    setShowFormModal(true);
  };

  const openEditModal = (rule: RuleResponse) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      description: rule.description || '',
      prompt: rule.prompt,
      threshold: rule.threshold,
      channel_ids: rule.channel_ids || [],
      is_active: rule.is_active,
    });
    setFormError(null);
    setShowFormModal(true);
  };

  const handleSubmit = async () => {
    if (!formData.name.trim()) {
      setFormError(t.rules.enterRuleName);
      return;
    }
    if (!formData.prompt.trim() || formData.prompt.length < 10) {
      setFormError(t.rules.enterPrompt);
      return;
    }

    try {
      setFormLoading(true);
      setFormError(null);

      const payload = {
        name: formData.name.trim(),
        description: formData.description.trim() || null,
        prompt: formData.prompt.trim(),
        threshold: formData.threshold,
        channel_ids: formData.channel_ids.length > 0 ? formData.channel_ids : null,
        is_active: formData.is_active,
        schedule: { always: true },
      };

      if (editingRule) {
        await rulesApi.updateRule(editingRule.id, payload);
      } else {
        await rulesApi.createRule(payload);
      }

      await loadData();
      setShowFormModal(false);
    } catch (err: any) {
      setFormError(err.response?.data?.detail || t.rules.failedToSave);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDelete = async (ruleId: string) => {
    if (!confirm(t.rules.confirmDelete)) {
      return;
    }

    try {
      await rulesApi.deleteRule(ruleId);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || t.rules.failedToDelete);
    }
  };

  const handleToggleActive = async (rule: RuleResponse) => {
    try {
      await rulesApi.toggleRuleActive(rule.id, rule.is_active);
      await loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || t.rules.failedToUpdate);
    }
  };

  const openTestModal = (rule: RuleResponse) => {
    setTestingRule(rule);
    setTestMessage('');
    setTestResult(null);
    setTestError(null);
    setShowTestModal(true);
  };

  const handleTest = async () => {
    if (!testMessage.trim()) {
      setTestError(t.rules.enterTestMessage);
      return;
    }

    try {
      setTestLoading(true);
      setTestError(null);
      const result = await rulesApi.testRule(testingRule!.id, {
        message_text: testMessage.trim(),
      });
      setTestResult(result);
    } catch (err: any) {
      setTestError(err.response?.data?.detail || t.rules.failedToTest);
    } finally {
      setTestLoading(false);
    }
  };

  const handleChannelToggle = (channelId: string) => {
    setFormData(prev => {
      const channelIds = prev.channel_ids.includes(channelId)
        ? prev.channel_ids.filter(id => id !== channelId)
        : [...prev.channel_ids, channelId];
      return { ...prev, channel_ids: channelIds };
    });
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">{t.rules.title}</h2>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                {t.rules.subtitle}
              </p>
            </div>
            <Button onClick={openAddModal}>
              {t.rules.addRule}
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
          ) : rules.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">{t.rules.noRules}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">{t.rules.noRulesDesc}</p>
                <Button onClick={openAddModal}>
                  {t.rules.createFirstRule}
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {rules.map((rule) => (
                <Card key={rule.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <CardTitle className="text-lg truncate">{rule.name}</CardTitle>
                        <CardDescription className="mt-1 line-clamp-2">
                          {rule.description || t.rules.noDescription}
                        </CardDescription>
                      </div>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ml-2 ${
                        rule.is_active
                          ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                      }`}>
                        {rule.is_active ? t.rules.active : t.rules.paused}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 text-sm mb-4">
                      <div>
                        <strong className="text-gray-900 dark:text-white">{t.rules.threshold}:</strong>{' '}
                        <span className="text-gray-700 dark:text-gray-300">{(rule.threshold * 100).toFixed(0)}%</span>
                      </div>
                      <div>
                        <strong className="text-gray-900 dark:text-white">{t.rules.sources}:</strong>{' '}
                        <span className="text-gray-700 dark:text-gray-300">
                          {rule.channel_ids && rule.channel_ids.length > 0
                            ? t.rules.sourcesSelected.replace('{{count}}', String(rule.channel_ids.length))
                            : t.rules.allSources}
                        </span>
                      </div>
                      <div>
                        <strong className="text-gray-900 dark:text-white">{t.rules.leadsFound}:</strong>{' '}
                        <span className="text-primary-600 dark:text-primary-400 font-medium">{rule.leads_count || 0}</span>
                      </div>
                      <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                        <div className="text-xs text-gray-500 dark:text-gray-400 line-clamp-3">
                          {rule.prompt}
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => openEditModal(rule)}
                      >
                        {t.common.edit}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => openTestModal(rule)}
                      >
                        {t.rules.test}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleToggleActive(rule)}
                      >
                        {rule.is_active ? t.rules.pause : t.rules.activate}
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(rule.id)}
                      >
                        {t.common.delete}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Add/Edit Rule Modal */}
          {showFormModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <Card className="w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
                <div className="overflow-y-auto">
                  <CardHeader>
                    <CardTitle>{editingRule ? t.rules.editRule : t.rules.addNewRule}</CardTitle>
                    <CardDescription>
                      {t.rules.ruleFormDesc}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                  {formError && <Alert variant="error">{formError}</Alert>}

                  <Input
                    label={t.rules.ruleName}
                    type="text"
                    placeholder="e.g., Python Developer Jobs"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    disabled={formLoading}
                  />

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t.rules.descriptionOptional}
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      rows={2}
                      placeholder={t.rules.descriptionPlaceholder}
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      disabled={formLoading}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t.rules.llmPrompt} <span className="text-red-500">*</span>
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
                      rows={6}
                      placeholder={t.rules.promptPlaceholder}
                      value={formData.prompt}
                      onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
                      disabled={formLoading}
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {t.rules.promptHelp}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      {t.rules.confidenceThreshold}: {(formData.threshold * 100).toFixed(0)}%
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={formData.threshold}
                      onChange={(e) => setFormData({ ...formData, threshold: parseFloat(e.target.value) })}
                      disabled={formLoading}
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {t.rules.thresholdHelp}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
                      {t.rules.applyToSources}
                    </label>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                      {t.rules.applyToSourcesHelp}
                    </p>
                    {subscriptions.length === 0 ? (
                      <Alert variant="info">
                        {t.rules.noSourcesAvailable}
                      </Alert>
                    ) : (
                      <div className="max-h-48 overflow-y-auto border border-gray-200 dark:border-gray-700 rounded-lg p-3 space-y-2">
                        {subscriptions.map((subscription) => (
                          <label key={subscription.channel_id} className="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 p-2 rounded">
                            <input
                              type="checkbox"
                              checked={formData.channel_ids.includes(subscription.channel_id)}
                              onChange={() => handleChannelToggle(subscription.channel_id)}
                              disabled={formLoading}
                              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                            />
                            <div className="flex-1">
                              <div className="font-medium text-sm text-gray-900 dark:text-white">{subscription.channel_title || subscription.channel_username}</div>
                              {subscription.channel_username && <div className="text-xs text-gray-500 dark:text-gray-400">@{subscription.channel_username}</div>}
                            </div>
                            <span className="text-xs text-gray-500 dark:text-gray-400">{subscription.channel_type}</span>
                          </label>
                        ))}
                      </div>
                    )}

                    {/* Информация о поведении системы */}
                    <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <div className="flex items-start gap-2">
                        <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="text-sm text-blue-800 dark:text-blue-300">
                          <p className="font-medium mb-1">Как работает анализ каналов:</p>
                          <ul className="space-y-1 ml-1">
                            <li>• При добавлении нового канала анализируются <strong>последние 5 дней</strong> истории (макс. 100 сообщений)</li>
                            <li>• После первого анализа обрабатываются только новые сообщения</li>
                            <li>• При изменении правила (промпт/порог/каналы) анализ начинается заново</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="is_active"
                      checked={formData.is_active}
                      onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                      disabled={formLoading}
                      className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label htmlFor="is_active" className="ml-2 block text-sm text-gray-900 dark:text-white">
                      {t.rules.activeStartMonitoring}
                    </label>
                  </div>

                  <div className="flex gap-2 pt-4">
                    <Button
                      variant="outline"
                      onClick={() => setShowFormModal(false)}
                      disabled={formLoading}
                      className="flex-1"
                    >
                      {t.common.cancel}
                    </Button>
                    <Button
                      onClick={handleSubmit}
                      loading={formLoading}
                      className="flex-1"
                    >
                      {editingRule ? t.rules.saveChanges : t.rules.createRule}
                    </Button>
                  </div>
                </CardContent>
                </div>
              </Card>
            </div>
          )}

          {/* Test Rule Modal */}
          {showTestModal && testingRule && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <Card className="w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                <div className="overflow-y-auto">
                  <CardHeader>
                    <CardTitle>Test Rule: {testingRule.name}</CardTitle>
                    <CardDescription>
                      Test how this rule would analyze a sample message
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                  {testError && <Alert variant="error">{testError}</Alert>}

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Sample Message
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                      rows={6}
                      placeholder="Paste a message to test against this rule..."
                      value={testMessage}
                      onChange={(e) => setTestMessage(e.target.value)}
                      disabled={testLoading}
                    />
                  </div>

                  {testResult && (
                    <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 dark:text-white">Match:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          testResult.is_match
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {testResult.is_match ? 'Yes' : 'No'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 dark:text-white">Confidence:</span>
                        <span className="text-lg font-bold text-primary-600">
                          {(testResult.confidence * 100).toFixed(1)}%
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900 dark:text-white">Would Create Lead:</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          testResult.would_create_lead
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {testResult.would_create_lead ? 'Yes' : 'No'}
                        </span>
                      </div>

                      <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                        <span className="font-medium text-gray-900 dark:text-white block mb-2">LLM Reasoning:</span>
                        <p className="text-sm text-gray-700 dark:text-gray-300 italic">{testResult.reasoning}</p>
                      </div>

                      {testResult.extracted_entities && (
                        <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                          <span className="font-medium text-gray-900 dark:text-white block mb-2">Extracted Entities:</span>
                          <div className="space-y-2 text-sm text-gray-900 dark:text-white">
                            {testResult.extracted_entities.contacts && testResult.extracted_entities.contacts.length > 0 && (
                              <div>
                                <strong>Contacts:</strong> {testResult.extracted_entities.contacts.join(', ')}
                              </div>
                            )}
                            {testResult.extracted_entities.keywords && testResult.extracted_entities.keywords.length > 0 && (
                              <div>
                                <strong>Keywords:</strong> {testResult.extracted_entities.keywords.join(', ')}
                              </div>
                            )}
                            {testResult.extracted_entities.budget && (
                              <div>
                                <strong>Budget:</strong> {testResult.extracted_entities.budget}
                              </div>
                            )}
                            {testResult.extracted_entities.deadline && (
                              <div>
                                <strong>Deadline:</strong> {testResult.extracted_entities.deadline}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2 pt-4">
                    <Button
                      variant="outline"
                      onClick={() => setShowTestModal(false)}
                      disabled={testLoading}
                      className="flex-1"
                    >
                      Close
                    </Button>
                    <Button
                      onClick={handleTest}
                      loading={testLoading}
                      className="flex-1"
                    >
                      Test Rule
                    </Button>
                  </div>
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
