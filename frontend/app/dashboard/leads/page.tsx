'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { leadsApi } from '@/lib/api/leads';
import { rulesApi } from '@/lib/api/rules';
import { telegramApi } from '@/lib/api/telegram';
import {
  LeadResponse,
  LeadWithDetails,
  LeadStatus,
  LeadStatusColors,
} from '@/lib/api/lead-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';
import { RuleResponse } from '@/lib/api/rule-types';
import { SubscriptionResponse } from '@/lib/api/telegram-types';

export default function LeadsPage() {
  const { t } = useLanguage();
  const searchParams = useSearchParams();

  // State для списка лидов
  const [leads, setLeads] = useState<LeadResponse[]>([]);
  const [rules, setRules] = useState<RuleResponse[]>([]);
  const [subscriptions, setSubscriptions] = useState<SubscriptionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // State для фильтров
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [ruleFilter, setRuleFilter] = useState<string>('all');
  const [channelFilter, setChannelFilter] = useState<string>('all');

  // State для пагинации
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [hasMore, setHasMore] = useState(true);

  // State для detail modal
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedLead, setSelectedLead] = useState<LeadWithDetails | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  // State для export
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadRulesAndSubscriptions();
  }, []);

  useEffect(() => {
    loadLeads();
  }, [statusFilter, ruleFilter, channelFilter, skip]);

  // Auto-open lead from URL parameter (deep link from Telegram notifications)
  useEffect(() => {
    const leadId = searchParams.get('lead_id');
    if (leadId && leads.length > 0) {
      // Find lead in current list
      const lead = leads.find(l => l.id === leadId);
      if (lead) {
        openDetailModal(lead);
      } else {
        // Lead not in current page, load it directly
        openDetailModalById(leadId);
      }
    }
  }, [searchParams, leads]);

  const loadRulesAndSubscriptions = async () => {
    try {
      const [rulesData, subscriptionsData] = await Promise.all([
        rulesApi.listRules(),
        telegramApi.listSubscriptions(),
      ]);
      setRules(rulesData);
      setSubscriptions(subscriptionsData);
    } catch (err: any) {
      console.error('Failed to load rules/subscriptions:', err);
    }
  };

  const loadLeads = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: any = {
        skip,
        limit,
      };

      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      if (ruleFilter !== 'all') {
        params.rule_id = ruleFilter;
      }
      if (channelFilter !== 'all') {
        params.channel_id = channelFilter;
      }

      const data = await leadsApi.listLeads(params);
      setLeads(data);
      setHasMore(data.length === limit);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

  const openDetailModal = async (lead: LeadResponse) => {
    setShowDetailModal(true);
    setDetailLoading(true);
    setDetailError(null);
    setSelectedLead(null);

    try {
      const details = await leadsApi.getLead(lead.id);
      setSelectedLead(details);
    } catch (err: any) {
      setDetailError(err.response?.data?.detail || 'Failed to load lead details');
    } finally {
      setDetailLoading(false);
    }
  };

  const openDetailModalById = async (leadId: string) => {
    setShowDetailModal(true);
    setDetailLoading(true);
    setDetailError(null);
    setSelectedLead(null);

    try {
      const details = await leadsApi.getLead(leadId);
      setSelectedLead(details);
    } catch (err: any) {
      setDetailError(err.response?.data?.detail || 'Failed to load lead details');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleStatusChange = async (leadId: string, newStatus: LeadStatus) => {
    try {
      await leadsApi.updateLeadStatus(leadId, newStatus);
      await loadLeads();

      // Update detail modal if open
      if (selectedLead && selectedLead.id === leadId) {
        const updated = await leadsApi.getLead(leadId);
        setSelectedLead(updated);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update lead status');
    }
  };

  const handleDelete = async (leadId: string) => {
    if (!confirm('Are you sure you want to delete this lead?')) {
      return;
    }

    try {
      await leadsApi.deleteLead(leadId);
      await loadLeads();
      if (selectedLead?.id === leadId) {
        setShowDetailModal(false);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete lead');
    }
  };

  const resetFilters = () => {
    setStatusFilter('all');
    setRuleFilter('all');
    setChannelFilter('all');
    setSkip(0);
  };

  const handleExport = async () => {
    try {
      setExporting(true);

      // Построить query params для экспорта
      const params = new URLSearchParams();
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (ruleFilter !== 'all') params.append('rule_id', ruleFilter);
      if (channelFilter !== 'all') params.append('channel_id', channelFilter);

      // Получить токен из localStorage
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      // Скачать файл
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/leads/export/csv?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Export failed');
      }

      // Получить blob и скачать
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `leads_export_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(err.message || 'Failed to export leads');
    } finally {
      setExporting(false);
    }
  };

  const handlePrevPage = () => {
    setSkip(Math.max(0, skip - limit));
  };

  const handleNextPage = () => {
    setSkip(skip + limit);
  };

  const getRuleName = (ruleId: string) => {
    const rule = rules.find(r => r.id === ruleId);
    return rule?.name || 'Unknown Rule';
  };

  const getChannelName = (channelId?: string | null) => {
    if (!channelId) return 'Unknown Channel';
    const subscription = subscriptions.find(s => s.channel_id === channelId);
    return subscription?.channel_title || subscription?.channel_username || 'Unknown Channel';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">{t.leads.title}</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {t.leads.subtitle}
            </p>
          </div>

          {/* Фильтры */}
          <Card>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t.leads.status}
                  </label>
                  <select
                    value={statusFilter}
                    onChange={(e) => {
                      setStatusFilter(e.target.value);
                      setSkip(0);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="all">{t.leads.allStatuses}</option>
                    {Object.values(LeadStatus).map((status) => (
                      <option key={status} value={status}>{t.leadStatus[status]}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t.leads.rule}
                  </label>
                  <select
                    value={ruleFilter}
                    onChange={(e) => {
                      setRuleFilter(e.target.value);
                      setSkip(0);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="all">{t.leads.allRules}</option>
                    {rules.map((rule) => (
                      <option key={rule.id} value={rule.id}>{rule.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    {t.leads.source}
                  </label>
                  <select
                    value={channelFilter}
                    onChange={(e) => {
                      setChannelFilter(e.target.value);
                      setSkip(0);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="all">{t.leads.allSources}</option>
                    {subscriptions.map((subscription) => (
                      <option key={subscription.channel_id} value={subscription.channel_id}>
                        {subscription.channel_title || subscription.channel_username}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {(statusFilter !== 'all' || ruleFilter !== 'all' || channelFilter !== 'all') && (
                <div className="mt-4 flex items-center gap-3">
                  <Button variant="outline" size="sm" onClick={resetFilters}>
                    {t.leads.resetFilters}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExport}
                    disabled={exporting}
                  >
                    {exporting ? t.leads.exporting : t.leads.exportCSV}
                  </Button>
                </div>
              )}
              {!(statusFilter !== 'all' || ruleFilter !== 'all' || channelFilter !== 'all') && (
                <div className="mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleExport}
                    disabled={exporting}
                  >
                    {exporting ? t.leads.exporting : t.leads.exportCSV}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {error && <Alert variant="error">{error}</Alert>}

          {/* Список лидов */}
          {loading ? (
            <div className="flex justify-center py-12">
              <svg className="animate-spin h-12 w-12 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            </div>
          ) : leads.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">{t.leads.noLeads}</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {statusFilter !== 'all' || ruleFilter !== 'all' || channelFilter !== 'all'
                    ? t.leads.tryAdjustingFilters
                    : t.leads.noLeadsDesc}
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {leads.map((lead) => (
                <Card key={lead.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="py-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2 flex-wrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${LeadStatusColors[lead.status]}`}>
                            {t.leadStatus[lead.status]}
                          </span>
                          <span className="text-sm font-medium text-primary-600 dark:text-primary-400">
                            {t.leads.score}: {(lead.score * 100).toFixed(0)}%
                          </span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            {formatDate(lead.created_at)}
                          </span>
                        </div>

                        <div className="mb-2">
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            {t.leads.matchedRule}: <span className="font-medium text-gray-900 dark:text-white">{getRuleName(lead.rule_id)}</span>
                          </span>
                        </div>

                        {lead.reasoning && (
                          <p className="text-sm text-gray-700 dark:text-gray-300 italic line-clamp-2 mb-2">
                            "{lead.reasoning}"
                          </p>
                        )}

                        {lead.extracted_entities?.summary && (
                          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                            {lead.extracted_entities.summary}
                          </p>
                        )}

                        {lead.extracted_entities?.contacts && lead.extracted_entities.contacts.length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {lead.extracted_entities.contacts.slice(0, 3).map((contact, idx) => (
                              <span key={idx} className="px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded break-all">
                                {contact}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <div className="ml-4 flex flex-col gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openDetailModal(lead)}
                        >
                          {t.leads.viewDetails}
                        </Button>

                        <select
                          value={lead.status}
                          onChange={(e) => handleStatusChange(lead.id, e.target.value as LeadStatus)}
                          className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                        >
                          {Object.values(LeadStatus).map((status) => (
                            <option key={status} value={status}>{t.leadStatus[status]}</option>
                          ))}
                        </select>

                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleDelete(lead.id)}
                        >
                          {t.common.delete}
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}

              {/* Пагинация */}
              <div className="flex items-center justify-between pt-4">
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  {t.leads.showing} {skip + 1} - {skip + leads.length}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handlePrevPage}
                    disabled={skip === 0}
                  >
                    {t.leads.previous}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleNextPage}
                    disabled={!hasMore}
                  >
                    {t.leads.next}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Lead Detail Modal */}
          {showDetailModal && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
              <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <CardHeader>
                  <CardTitle>{t.leads.leadDetails}</CardTitle>
                  <CardDescription>
                    {t.leads.completeInformation}
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {detailError && <Alert variant="error">{detailError}</Alert>}

                  {detailLoading ? (
                    <div className="flex justify-center py-8">
                      <svg className="animate-spin h-8 w-8 text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                    </div>
                  ) : selectedLead && (
                    <>
                      {/* Status and Score */}
                      <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <div className="flex items-center gap-4">
                          <span className={`px-3 py-1 text-sm font-medium rounded-full ${LeadStatusColors[selectedLead.status]}`}>
                            {t.leadStatus[selectedLead.status]}
                          </span>
                          <div>
                            <div className="text-sm text-gray-600 dark:text-gray-400">{t.leads.confidenceScore}</div>
                            <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                              {(selectedLead.score * 100).toFixed(1)}%
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600 dark:text-gray-400">{t.leads.created}</div>
                          <div className="font-medium">{formatDate(selectedLead.created_at)}</div>
                        </div>
                      </div>

                      {/* Message */}
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white mb-2">{t.leads.message}</h3>
                        <div className="p-4 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <div className="text-sm font-medium text-gray-900 dark:text-white">
                                {selectedLead.channel_title || t.leads.unknownSource}
                              </div>
                              {selectedLead.channel_username && (
                                <div className="text-xs text-gray-500 dark:text-gray-400">@{selectedLead.channel_username}</div>
                              )}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {selectedLead.message_date && formatDate(selectedLead.message_date)}
                            </div>
                          </div>
                          <div className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                            {selectedLead.message_text || t.leads.noMessageText}
                          </div>
                          {selectedLead.message_views_count && (
                            <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
                              {t.leads.views}: {selectedLead.message_views_count.toLocaleString()}
                            </div>
                          )}
                          {selectedLead.message_links && selectedLead.message_links.length > 0 && (
                            <div className="mt-3">
                              <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{t.leads.links}:</div>
                              {selectedLead.message_links.map((link, idx) => (
                                <a
                                  key={idx}
                                  href={link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="block text-xs text-primary-600 dark:text-primary-400 hover:underline truncate"
                                >
                                  {link}
                                </a>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* LLM Analysis */}
                      {selectedLead.reasoning && (
                        <div>
                          <h3 className="font-medium text-gray-900 dark:text-white mb-2">{t.leads.llmAnalysis}</h3>
                          <div className="p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-700 rounded-lg">
                            <p className="text-sm text-gray-700 dark:text-gray-300 italic">{selectedLead.reasoning}</p>
                          </div>
                        </div>
                      )}

                      {/* Extracted Entities */}
                      {selectedLead.extracted_entities && (
                        <div>
                          <h3 className="font-medium text-gray-900 dark:text-white mb-2">{t.leads.extractedInformation}</h3>
                          <div className="p-4 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg space-y-3">
                            {selectedLead.extracted_entities.contacts && selectedLead.extracted_entities.contacts.length > 0 && (
                              <div>
                                <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t.leads.contacts}:</div>
                                <div className="flex flex-wrap gap-2">
                                  {selectedLead.extracted_entities.contacts.map((contact, idx) => (
                                    <span key={idx} className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400 text-xs rounded">
                                      {contact}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {selectedLead.extracted_entities.keywords && selectedLead.extracted_entities.keywords.length > 0 && (
                              <div>
                                <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t.leads.keywords}:</div>
                                <div className="flex flex-wrap gap-2">
                                  {selectedLead.extracted_entities.keywords.map((keyword, idx) => (
                                    <span key={idx} className="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 text-xs rounded">
                                      {keyword}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {selectedLead.extracted_entities.budget && (
                              <div>
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t.leads.budget}: </span>
                                <span className="text-sm text-gray-900 dark:text-white">{selectedLead.extracted_entities.budget}</span>
                              </div>
                            )}
                            {selectedLead.extracted_entities.deadline && (
                              <div>
                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{t.leads.deadline}: </span>
                                <span className="text-sm text-gray-900 dark:text-white">{selectedLead.extracted_entities.deadline}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Rule */}
                      <div>
                        <h3 className="font-medium text-gray-900 dark:text-white mb-2">{t.leads.matchedRule}</h3>
                        <div className="p-4 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg">
                          <div className="font-medium text-gray-900 dark:text-white mb-1">
                            {selectedLead.rule_name || t.leads.unknownRule}
                          </div>
                          {selectedLead.rule_prompt && (
                            <div className="text-sm text-gray-600 dark:text-gray-400 line-clamp-3">
                              {selectedLead.rule_prompt}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                        {selectedLead.telegram_message_link && (
                          <a
                            href={selectedLead.telegram_message_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1"
                          >
                            <Button variant="outline" className="w-full">
                              {t.leads.openInTelegram}
                            </Button>
                          </a>
                        )}
                        <Button
                          variant="outline"
                          onClick={() => setShowDetailModal(false)}
                          className="flex-1"
                        >
                          {t.common.close}
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
