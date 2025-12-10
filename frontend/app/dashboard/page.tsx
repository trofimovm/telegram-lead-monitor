'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuth } from '@/lib/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { leadsApi } from '@/lib/api/leads';
import { rulesApi } from '@/lib/api/rules';
import { telegramApi } from '@/lib/api/telegram';
import { analyticsApi } from '@/lib/api/analytics';
import { LeadStats, LeadStatus, LeadStatusColors } from '@/lib/api/lead-types';
import { LeadResponse } from '@/lib/api/lead-types';
import { ActivityTrendsResponse } from '@/lib/api/analytics-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { t } = useLanguage();

  const [stats, setStats] = useState<LeadStats | null>(null);
  const [sourcesCount, setSourcesCount] = useState(0);
  const [rulesCount, setRulesCount] = useState(0);
  const [recentLeads, setRecentLeads] = useState<LeadResponse[]>([]);
  const [activityTrends, setActivityTrends] = useState<ActivityTrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null); // Clear previous errors
      const [statsData, sourcesData, rulesData, leadsData, trendsData] = await Promise.all([
        leadsApi.getLeadStats(),
        telegramApi.listSubscriptions(), // Get all subscriptions
        rulesApi.listRules(true), // Only active rules
        leadsApi.listLeads({ limit: 5 }), // Last 5 leads
        analyticsApi.getActivityTrends(), // Activity trends
      ]);

      setStats(statsData);
      setSourcesCount(sourcesData.filter(s => s.is_active).length); // Filter active sources
      setRulesCount(rulesData.length);
      setRecentLeads(leadsData);
      setActivityTrends(trendsData);
    } catch (error: any) {
      console.error('Failed to load dashboard data:', error);
      setError(error.message || 'Не удалось загрузить данные дашборда');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t.time.justNow;
    if (diffMins < 60) return t.time.minutesAgo.replace('{{count}}', String(diffMins));
    if (diffHours < 24) return t.time.hoursAgo.replace('{{count}}', String(diffHours));
    return t.time.daysAgo.replace('{{count}}', String(diffDays));
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
              {t.dashboard.welcomeBack.replace('{{name}}', user?.full_name || '')}
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {t.dashboard.subtitle}
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">
              <p className="text-sm font-medium mb-2">⚠️ {error}</p>
              <button
                onClick={loadDashboardData}
                className="text-sm underline hover:no-underline font-medium"
              >
                Попробовать снова
              </button>
            </div>
          )}

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t.dashboard.activeSources}</CardTitle>
                <CardDescription>{t.dashboard.activeSourcesDesc}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-primary-600">
                  {loading ? '-' : sourcesCount}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t.dashboard.activeRules}</CardTitle>
                <CardDescription>{t.dashboard.activeRulesDesc}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-primary-600">
                  {loading ? '-' : rulesCount}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t.dashboard.totalLeads}</CardTitle>
                <CardDescription>{t.dashboard.totalLeadsDesc}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-primary-600">
                  {loading ? '-' : stats?.total || 0}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">{t.dashboard.recentLeads}</CardTitle>
                <CardDescription>{t.dashboard.recentLeadsDesc}</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-4xl font-bold text-green-600">
                  {loading ? '-' : stats?.recent_count || 0}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Activity Trends */}
          {activityTrends && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{t.dashboard.activityTrends}</CardTitle>
                    <CardDescription>{activityTrends.period}</CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push('/dashboard/analytics')}
                  >
                    {t.dashboard.viewAnalytics}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {[activityTrends.leads_trend, activityTrends.messages_trend, activityTrends.conversion_trend].map((trend, i) => (
                    <div key={i} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{trend.metric_name}</p>
                      <div className="flex items-baseline gap-3">
                        <p className="text-2xl font-bold text-gray-900 dark:text-white">{trend.current_value}</p>
                        <span className={`text-sm font-medium ${
                          trend.trend_direction === 'up' ? 'text-green-600' :
                          trend.trend_direction === 'down' ? 'text-red-600' : 'text-gray-600 dark:text-gray-400'
                        }`}>
                          {trend.trend_direction === 'up' ? '↑' : trend.trend_direction === 'down' ? '↓' : '→'}
                          {Math.abs(trend.change_percentage).toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {t.dashboard.vsPreviously.replace('{{value}}', String(trend.previous_value))}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Leads by Status */}
          {stats && stats.total > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>{t.dashboard.leadsByStatus}</CardTitle>
                <CardDescription>{t.dashboard.leadsByStatusDesc}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {Object.entries(stats.by_status).map(([status, count]) => (
                    <div key={status} className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900 dark:text-white">{count}</div>
                      <div className={`text-sm mt-1 px-2 py-1 rounded-full inline-block ${LeadStatusColors[status as LeadStatus]}`}>
                        {t.leadStatus[status as LeadStatus]}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Leads Widget */}
          {recentLeads.length > 0 && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>{t.dashboard.recentLeadsWidget}</CardTitle>
                    <CardDescription>{t.dashboard.recentLeadsWidgetDesc}</CardDescription>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push('/dashboard/leads')}
                  >
                    {t.dashboard.viewAll}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentLeads.map((lead) => (
                    <div
                      key={lead.id}
                      className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer transition-colors"
                      onClick={() => router.push('/dashboard/leads')}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${LeadStatusColors[lead.status]}`}>
                            {t.leadStatus[lead.status]}
                          </span>
                          <span className="text-xs font-medium text-primary-600 dark:text-primary-400">
                            {(lead.score * 100).toFixed(0)}%
                          </span>
                        </div>
                        {lead.reasoning && (
                          <p className="text-sm text-gray-700 dark:text-gray-300 line-clamp-1 italic">
                            "{lead.reasoning}"
                          </p>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400 ml-4">
                        {formatDate(lead.created_at)}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>{t.quickActions.title}</CardTitle>
              <CardDescription>
                {t.quickActions.subtitle}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center font-semibold">
                    1
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">{t.quickActions.step1Title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {t.quickActions.step1Desc}
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push('/dashboard/telegram-accounts')}
                    >
                      {t.quickActions.step1Button}
                    </Button>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center font-semibold">
                    2
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">{t.quickActions.step2Title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {t.quickActions.step2Desc}
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push('/dashboard/sources')}
                    >
                      {t.quickActions.step2Button}
                    </Button>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-full flex items-center justify-center font-semibold">
                    3
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">{t.quickActions.step3Title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {t.quickActions.step3Desc}
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push('/dashboard/rules')}
                    >
                      {t.quickActions.step3Button}
                    </Button>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-full flex items-center justify-center font-semibold">
                    4
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 dark:text-white">{t.quickActions.step4Title}</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                      {t.quickActions.step4Desc}
                    </p>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => router.push('/dashboard/leads')}
                    >
                      {t.quickActions.step4Button}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
