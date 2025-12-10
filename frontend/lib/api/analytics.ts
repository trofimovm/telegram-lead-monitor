import { apiClient } from './client';
import {
  TimeGranularity,
  LeadsTimeSeriesResponse,
  ConversionFunnelResponse,
  ChannelPerformanceResponse,
  RulePerformanceResponse,
  ActivityTrendsResponse,
  AnalyticsSummaryResponse,
} from './analytics-types';

/**
 * API клиент для Analytics
 */
export const analyticsApi = {
  /**
   * Получить сводку аналитики
   */
  getSummary: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<AnalyticsSummaryResponse> => {
    return apiClient.get<AnalyticsSummaryResponse>('/analytics/summary', { params });
  },

  /**
   * Получить временной ряд создания лидов
   */
  getLeadsTimeSeries: async (params?: {
    date_from?: string;
    date_to?: string;
    granularity?: TimeGranularity;
  }): Promise<LeadsTimeSeriesResponse> => {
    return apiClient.get<LeadsTimeSeriesResponse>('/analytics/leads-time-series', { params });
  },

  /**
   * Получить воронку конверсии
   */
  getConversionFunnel: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<ConversionFunnelResponse> => {
    return apiClient.get<ConversionFunnelResponse>('/analytics/conversion-funnel', { params });
  },

  /**
   * Получить производительность каналов
   */
  getChannelPerformance: async (params?: {
    date_from?: string;
    date_to?: string;
  }): Promise<ChannelPerformanceResponse> => {
    return apiClient.get<ChannelPerformanceResponse>('/analytics/channel-performance', { params });
  },

  /**
   * Получить производительность правил
   */
  getRulePerformance: async (): Promise<RulePerformanceResponse> => {
    return apiClient.get<RulePerformanceResponse>('/analytics/rule-performance');
  },

  /**
   * Получить тренды активности
   */
  getActivityTrends: async (): Promise<ActivityTrendsResponse> => {
    return apiClient.get<ActivityTrendsResponse>('/analytics/activity-trends');
  },
};
