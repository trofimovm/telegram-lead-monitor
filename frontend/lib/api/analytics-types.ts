/**
 * TypeScript типы для Analytics API.
 */

export enum TimeGranularity {
  HOUR = 'hour',
  DAY = 'day',
  WEEK = 'week',
  MONTH = 'month',
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  date_label: string;
  count: number;
}

export interface LeadsTimeSeriesResponse {
  granularity: TimeGranularity;
  data_points: TimeSeriesDataPoint[];
  total_count: number;
  period_start: string;
  period_end: string;
}

export interface ConversionFunnelStage {
  stage_name: string;
  count: number;
  percentage: number;
  conversion_rate?: number | null;
}

export interface ConversionFunnelResponse {
  stages: ConversionFunnelStage[];
  total_leads: number;
  final_conversion_rate: number;
}

export interface ChannelPerformance {
  channel_id: string;
  channel_title: string;
  channel_username?: string | null;
  total_messages: number;
  total_leads: number;
  conversion_rate: number;
  avg_lead_score: number;
  last_message_date?: string | null;
}

export interface ChannelPerformanceResponse {
  channels: ChannelPerformance[];
  total_channels: number;
}

export interface RulePerformance {
  rule_id: string;
  rule_name: string;
  total_leads: number;
  avg_lead_score: number;
  leads_last_7d: number;
  leads_last_30d: number;
  is_active: boolean;
}

export interface RulePerformanceResponse {
  rules: RulePerformance[];
  total_rules: number;
}

export interface ActivityTrend {
  metric_name: string;
  current_value: number;
  previous_value: number;
  change_percentage: number;
  trend_direction: 'up' | 'down' | 'stable';
}

export interface ActivityTrendsResponse {
  leads_trend: ActivityTrend;
  messages_trend: ActivityTrend;
  conversion_trend: ActivityTrend;
  period: string;
}

export interface TopPerformer {
  id: string;
  name: string;
  type: 'channel' | 'rule';
  metric_value: number;
  metric_name: string;
}

export interface AnalyticsSummaryResponse {
  total_leads: number;
  total_messages: number;
  total_channels: number;
  total_rules: number;
  avg_lead_score: number;
  conversion_rate: number;
  top_channel?: TopPerformer | null;
  top_rule?: TopPerformer | null;
  period_start: string;
  period_end: string;
}
