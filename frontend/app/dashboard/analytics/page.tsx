'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DashboardLayout } from '@/components/layouts/DashboardLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { SimpleLineChart } from '@/components/charts/SimpleLineChart';
import { analyticsApi } from '@/lib/api/analytics';
import {
  AnalyticsSummaryResponse,
  LeadsTimeSeriesResponse,
  ConversionFunnelResponse,
  ChannelPerformanceResponse,
  RulePerformanceResponse,
  ActivityTrendsResponse,
  TimeGranularity,
} from '@/lib/api/analytics-types';
import { useLanguage } from '@/lib/contexts/LanguageContext';

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<AnalyticsSummaryResponse | null>(null);
  const [timeSeries, setTimeSeries] = useState<LeadsTimeSeriesResponse | null>(null);
  const [conversionFunnel, setConversionFunnel] = useState<ConversionFunnelResponse | null>(null);
  const [channelPerformance, setChannelPerformance] = useState<ChannelPerformanceResponse | null>(null);
  const [rulePerformance, setRulePerformance] = useState<RulePerformanceResponse | null>(null);
  const [activityTrends, setActivityTrends] = useState<ActivityTrendsResponse | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [summaryData, timeSeriesData, funnelData, channelData, ruleData, trendsData] = await Promise.all([
        analyticsApi.getSummary(),
        analyticsApi.getLeadsTimeSeries({ granularity: TimeGranularity.DAY }),
        analyticsApi.getConversionFunnel(),
        analyticsApi.getChannelPerformance(),
        analyticsApi.getRulePerformance(),
        analyticsApi.getActivityTrends(),
      ]);

      setSummary(summaryData);
      setTimeSeries(timeSeriesData);
      setConversionFunnel(funnelData);
      setChannelPerformance(channelData);
      setRulePerformance(ruleData);
      setActivityTrends(trendsData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (direction: string) => {
    if (direction === 'up') return '↑';
    if (direction === 'down') return '↓';
    return '→';
  };

  const getTrendColor = (direction: string) => {
    if (direction === 'up') return 'text-green-600';
    if (direction === 'down') return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <ProtectedRoute>
      <DashboardLayout>
        <div className="space-y-6">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white">{t.analytics.title}</h2>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              {t.analytics.subtitle}
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <p className="text-gray-500">{t.analytics.loadingAnalytics}</p>
            </div>
          ) : (
            <>
              {/* Summary Cards */}
              {summary && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">{t.analytics.totalLeads}</CardTitle>
                      <CardDescription>{t.analytics.last30Days}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-4xl font-bold text-primary-600">{summary.total_leads}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">{t.analytics.messagesCollected}</CardTitle>
                      <CardDescription>{t.analytics.last30Days}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-4xl font-bold text-primary-600">{summary.total_messages}</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">{t.analytics.conversion}</CardTitle>
                      <CardDescription>{t.analytics.messagesToLeads}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-4xl font-bold text-green-600">{summary.conversion_rate.toFixed(2)}%</p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">{t.analytics.avgScore}</CardTitle>
                      <CardDescription>{t.analytics.leadQuality}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-4xl font-bold text-purple-600">{(summary.avg_lead_score * 100).toFixed(0)}%</p>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Activity Trends */}
              {activityTrends && (
                <Card>
                  <CardHeader>
                    <CardTitle>{t.analytics.activityTrends}</CardTitle>
                    <CardDescription>{activityTrends.period}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {[activityTrends.leads_trend, activityTrends.messages_trend, activityTrends.conversion_trend].map((trend, i) => (
                        <div key={i} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{trend.metric_name}</p>
                          <div className="flex items-baseline gap-3">
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">{trend.current_value}</p>
                            <span className={`text-sm font-medium ${getTrendColor(trend.trend_direction)}`}>
                              {getTrendIcon(trend.trend_direction)} {Math.abs(trend.change_percentage).toFixed(1)}%
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {t.analytics.previous}: {trend.previous_value}
                          </p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Leads Time Series Chart */}
              {timeSeries && timeSeries.data_points.length > 0 && (
                <SimpleLineChart
                  title={t.analytics.leadsOverTime}
                  data={timeSeries.data_points.map(dp => ({
                    label: dp.date_label,
                    value: dp.count,
                  }))}
                  color="#4F46E5"
                />
              )}

              {/* Conversion Funnel */}
              {conversionFunnel && (
                <Card>
                  <CardHeader>
                    <CardTitle>{t.analytics.conversionFunnel}</CardTitle>
                    <CardDescription>
                      {t.analytics.totalConversion}: {conversionFunnel.final_conversion_rate.toFixed(2)}%
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {conversionFunnel.stages.map((stage, i) => (
                        <div key={i}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-900 dark:text-white capitalize">
                              {stage.stage_name.replace('_', ' ')}
                            </span>
                            <div className="flex items-center gap-3">
                              <span className="text-sm text-gray-600 dark:text-gray-400">{stage.count} {t.analytics.leads}</span>
                              {stage.conversion_rate !== null && (
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  ({stage.conversion_rate.toFixed(1)}% {t.analytics.conversionRate})
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-8">
                            <div
                              className="bg-primary-600 h-8 rounded-full flex items-center justify-end pr-3"
                              style={{ width: `${stage.percentage}%` }}
                            >
                              <span className="text-xs font-medium text-white">
                                {stage.percentage.toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Top Performers */}
              {summary && (summary.top_channel || summary.top_rule) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {summary.top_channel && (
                    <Card>
                      <CardHeader>
                        <CardTitle>{t.analytics.topSource}</CardTitle>
                        <CardDescription>{t.analytics.mostLeads}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-xl font-bold text-gray-900 dark:text-white truncate">{summary.top_channel.name}</p>
                        <p className="text-3xl font-bold text-primary-600 mt-2">
                          {summary.top_channel.metric_value} {summary.top_channel.metric_name}
                        </p>
                      </CardContent>
                    </Card>
                  )}

                  {summary.top_rule && (
                    <Card>
                      <CardHeader>
                        <CardTitle>{t.analytics.topRule}</CardTitle>
                        <CardDescription>{t.analytics.mostLeads}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <p className="text-xl font-bold text-gray-900 dark:text-white truncate">{summary.top_rule.name}</p>
                        <p className="text-3xl font-bold text-primary-600 mt-2">
                          {summary.top_rule.metric_value} {summary.top_rule.metric_name}
                        </p>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}

              {/* Source Performance Table */}
              {channelPerformance && channelPerformance.channels.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>{t.analytics.channelPerformance}</CardTitle>
                    <CardDescription>{t.analytics.topSources.replace('{N}', String(channelPerformance.channels.length))}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead>
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t.analytics.source}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.messages}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.leads}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.conversion}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.avgScore}</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {channelPerformance.channels.slice(0, 10).map((channel) => (
                            <tr key={channel.channel_id} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white max-w-xs truncate">{channel.channel_title}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{channel.total_messages}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{channel.total_leads}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{channel.conversion_rate.toFixed(2)}%</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{channel.avg_lead_score.toFixed(2)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Rule Performance Table */}
              {rulePerformance && rulePerformance.rules.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>{t.analytics.rulePerformance}</CardTitle>
                    <CardDescription>{t.analytics.allRules}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead>
                          <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">{t.analytics.rule}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.totalLeadsLabel}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.last7Days}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.last30DaysLabel}</th>
                            <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{t.analytics.avgScore}</th>
                            <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">{t.analytics.status}</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {rulePerformance.rules.map((rule) => (
                            <tr key={rule.rule_id} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-white max-w-xs truncate">{rule.rule_name}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{rule.total_leads}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{rule.leads_last_7d}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{rule.leads_last_30d}</td>
                              <td className="px-4 py-3 text-sm text-gray-600 text-right">{rule.avg_lead_score.toFixed(2)}</td>
                              <td className="px-4 py-3 text-center">
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                  rule.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                                }`}>
                                  {rule.is_active ? t.analytics.active : t.analytics.inactive}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </div>
      </DashboardLayout>
    </ProtectedRoute>
  );
}
