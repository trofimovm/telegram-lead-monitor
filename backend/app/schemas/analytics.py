"""
Pydantic schemas для Analytics (аналитика и статистика).
"""

from datetime import datetime, date
from typing import List, Dict, Optional
from enum import Enum

from pydantic import BaseModel, Field


class TimeGranularity(str, Enum):
    """Гранулярность временных данных"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class TimeSeriesDataPoint(BaseModel):
    """Точка данных для временного ряда"""
    timestamp: datetime = Field(..., description="Временная метка")
    date_label: str = Field(..., description="Метка даты для отображения (e.g., '2024-01-15')")
    count: int = Field(..., description="Количество событий")


class LeadsTimeSeriesResponse(BaseModel):
    """Временной ряд создания лидов"""
    granularity: TimeGranularity
    data_points: List[TimeSeriesDataPoint]
    total_count: int = Field(..., description="Общее количество за период")
    period_start: datetime
    period_end: datetime


class ConversionFunnelStage(BaseModel):
    """Этап воронки конверсии"""
    stage_name: str = Field(..., description="Название этапа (new, in_progress, processed)")
    count: int = Field(..., description="Количество лидов на этапе")
    percentage: float = Field(..., description="Процент от начального этапа")
    conversion_rate: Optional[float] = Field(None, description="Конверсия к предыдущему этапу")


class ConversionFunnelResponse(BaseModel):
    """Воронка конверсии лидов"""
    stages: List[ConversionFunnelStage]
    total_leads: int = Field(..., description="Всего лидов в начале воронки")
    final_conversion_rate: float = Field(..., description="Общая конверсия (processed / new)")


class ChannelPerformance(BaseModel):
    """Производительность канала"""
    channel_id: str
    channel_title: str
    channel_username: Optional[str] = None
    total_messages: int = Field(..., description="Всего сообщений собрано")
    total_leads: int = Field(..., description="Всего лидов создано")
    conversion_rate: float = Field(..., description="Конверсия сообщений в лиды")
    avg_lead_score: float = Field(..., description="Средний score лидов")
    last_message_date: Optional[datetime] = Field(None, description="Дата последнего сообщения")


class ChannelPerformanceResponse(BaseModel):
    """Список производительности каналов"""
    channels: List[ChannelPerformance]
    total_channels: int


class RulePerformance(BaseModel):
    """Производительность правила"""
    rule_id: str
    rule_name: str
    total_leads: int = Field(..., description="Всего лидов создано")
    avg_lead_score: float = Field(..., description="Средний score лидов")
    leads_last_7d: int = Field(..., description="Лидов за последние 7 дней")
    leads_last_30d: int = Field(..., description="Лидов за последние 30 дней")
    is_active: bool


class RulePerformanceResponse(BaseModel):
    """Список производительности правил"""
    rules: List[RulePerformance]
    total_rules: int


class ActivityTrend(BaseModel):
    """Тренд активности"""
    metric_name: str = Field(..., description="Название метрики")
    current_value: int = Field(..., description="Текущее значение")
    previous_value: int = Field(..., description="Предыдущее значение")
    change_percentage: float = Field(..., description="Процент изменения")
    trend_direction: str = Field(..., description="up, down, или stable")


class ActivityTrendsResponse(BaseModel):
    """Тренды активности"""
    leads_trend: ActivityTrend = Field(..., description="Тренд создания лидов")
    messages_trend: ActivityTrend = Field(..., description="Тренд сбора сообщений")
    conversion_trend: ActivityTrend = Field(..., description="Тренд конверсии")
    period: str = Field(..., description="Период сравнения (e.g., 'Last 7 days vs Previous 7 days')")


class TopPerformer(BaseModel):
    """Топ исполнитель"""
    id: str
    name: str
    type: str = Field(..., description="channel или rule")
    metric_value: int = Field(..., description="Значение метрики")
    metric_name: str = Field(..., description="Название метрики")


class AnalyticsSummaryResponse(BaseModel):
    """Сводка аналитики"""
    total_leads: int
    total_messages: int
    total_channels: int
    total_rules: int
    avg_lead_score: float
    conversion_rate: float = Field(..., description="Сообщений → Лиды")
    top_channel: Optional[TopPerformer] = None
    top_rule: Optional[TopPerformer] = None
    period_start: datetime
    period_end: datetime


class DateRangeRequest(BaseModel):
    """Запрос с диапазоном дат"""
    date_from: Optional[datetime] = Field(None, description="Начало периода (default: 30 days ago)")
    date_to: Optional[datetime] = Field(None, description="Конец периода (default: now)")
    granularity: TimeGranularity = Field(TimeGranularity.DAY, description="Гранулярность данных")
