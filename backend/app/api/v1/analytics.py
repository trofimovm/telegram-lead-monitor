"""
API endpoints для Analytics (аналитика и статистика).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case, desc
from typing import Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.models.user import User
from app.models.tenant import Tenant
from app.models.lead import Lead
from app.models.global_message import GlobalMessage
from app.models.global_channel import GlobalChannel
from app.models.channel_subscription import ChannelSubscription
from app.models.rule import Rule
from app.schemas.analytics import (
    TimeGranularity,
    TimeSeriesDataPoint,
    LeadsTimeSeriesResponse,
    ConversionFunnelStage,
    ConversionFunnelResponse,
    ChannelPerformance,
    ChannelPerformanceResponse,
    RulePerformance,
    RulePerformanceResponse,
    ActivityTrend,
    ActivityTrendsResponse,
    TopPerformer,
    AnalyticsSummaryResponse,
    DateRangeRequest,
)
from app.api.deps import get_db, get_current_active_user, get_current_tenant

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить сводку аналитики за период.
    """
    # Дефолтные даты: последние 30 дней
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    # Total leads
    total_leads = db.query(func.count(Lead.id)).filter(
        and_(
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).scalar() or 0

    # Total messages (через subscriptions tenant'а)
    total_messages = db.query(func.count(GlobalMessage.id)).join(
        ChannelSubscription,
        ChannelSubscription.channel_id == GlobalMessage.channel_id
    ).filter(
        and_(
            ChannelSubscription.tenant_id == current_tenant.id,
            GlobalMessage.created_at >= date_from,
            GlobalMessage.created_at <= date_to
        )
    ).scalar() or 0

    # Total channels (подписки tenant'а)
    total_channels = db.query(func.count(ChannelSubscription.id)).filter(
        ChannelSubscription.tenant_id == current_tenant.id
    ).scalar() or 0

    # Total rules
    total_rules = db.query(func.count(Rule.id)).filter(
        Rule.tenant_id == current_tenant.id
    ).scalar() or 0

    # Avg lead score
    avg_lead_score = db.query(func.avg(Lead.score)).filter(
        and_(
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).scalar() or Decimal("0.0")

    # Conversion rate
    conversion_rate = (total_leads / total_messages * 100) if total_messages > 0 else 0.0

    # Top channel by leads
    top_channel_data = db.query(
        GlobalChannel.id,
        GlobalChannel.title,
        func.count(Lead.id).label('lead_count')
    ).join(
        GlobalMessage, GlobalMessage.channel_id == GlobalChannel.id
    ).join(
        Lead, Lead.global_message_id == GlobalMessage.id
    ).join(
        ChannelSubscription,
        ChannelSubscription.channel_id == GlobalChannel.id
    ).filter(
        and_(
            ChannelSubscription.tenant_id == current_tenant.id,
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).group_by(GlobalChannel.id, GlobalChannel.title).order_by(desc('lead_count')).first()

    top_channel = None
    if top_channel_data:
        top_channel = TopPerformer(
            id=str(top_channel_data[0]),
            name=top_channel_data[1],
            type="channel",
            metric_value=top_channel_data[2],
            metric_name="leads"
        )

    # Top rule by leads
    top_rule_data = db.query(
        Rule.id,
        Rule.name,
        func.count(Lead.id).label('lead_count')
    ).join(Lead).filter(
        and_(
            Rule.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).group_by(Rule.id, Rule.name).order_by(desc('lead_count')).first()

    top_rule = None
    if top_rule_data:
        top_rule = TopPerformer(
            id=str(top_rule_data[0]),
            name=top_rule_data[1],
            type="rule",
            metric_value=top_rule_data[2],
            metric_name="leads"
        )

    return AnalyticsSummaryResponse(
        total_leads=total_leads,
        total_messages=total_messages,
        total_channels=total_channels,
        total_rules=total_rules,
        avg_lead_score=float(avg_lead_score),
        conversion_rate=round(conversion_rate, 2),
        top_channel=top_channel,
        top_rule=top_rule,
        period_start=date_from,
        period_end=date_to
    )


@router.get("/leads-time-series", response_model=LeadsTimeSeriesResponse)
async def get_leads_time_series(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    granularity: TimeGranularity = Query(TimeGranularity.DAY),
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить временной ряд создания лидов.
    """
    # Дефолтные даты
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    # Определяем формат группировки по гранулярности
    if granularity == TimeGranularity.HOUR:
        trunc_func = func.date_trunc('hour', Lead.created_at)
        date_format = '%Y-%m-%d %H:00'
    elif granularity == TimeGranularity.DAY:
        trunc_func = func.date_trunc('day', Lead.created_at)
        date_format = '%Y-%m-%d'
    elif granularity == TimeGranularity.WEEK:
        trunc_func = func.date_trunc('week', Lead.created_at)
        date_format = '%Y Week %W'
    else:  # MONTH
        trunc_func = func.date_trunc('month', Lead.created_at)
        date_format = '%Y-%m'

    # Query для временного ряда
    time_series_data = db.query(
        trunc_func.label('period'),
        func.count(Lead.id).label('count')
    ).filter(
        and_(
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).group_by('period').order_by('period').all()

    # Формируем data points
    data_points = [
        TimeSeriesDataPoint(
            timestamp=period,
            date_label=period.strftime(date_format),
            count=count
        )
        for period, count in time_series_data
    ]

    total_count = sum(dp.count for dp in data_points)

    return LeadsTimeSeriesResponse(
        granularity=granularity,
        data_points=data_points,
        total_count=total_count,
        period_start=date_from,
        period_end=date_to
    )


@router.get("/conversion-funnel", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить воронку конверсии лидов по статусам.
    """
    # Дефолтные даты
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    # Получаем количество по каждому статусу
    status_counts = db.query(
        Lead.status,
        func.count(Lead.id).label('count')
    ).filter(
        and_(
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).group_by(Lead.status).all()

    status_dict = {status: count for status, count in status_counts}

    # Определяем порядок этапов воронки
    funnel_order = ['new', 'in_progress', 'processed']

    total_leads = status_dict.get('new', 0)
    stages = []
    prev_count = None

    for status_name in funnel_order:
        count = status_dict.get(status_name, 0)

        # Процент от начального этапа
        percentage = (count / total_leads * 100) if total_leads > 0 else 0.0

        # Конверсия к предыдущему этапу
        conversion_rate = None
        if prev_count is not None and prev_count > 0:
            conversion_rate = (count / prev_count * 100)

        stages.append(ConversionFunnelStage(
            stage_name=status_name,
            count=count,
            percentage=round(percentage, 2),
            conversion_rate=round(conversion_rate, 2) if conversion_rate is not None else None
        ))

        prev_count = count

    # Общая конверсия (processed / new)
    final_conversion_rate = (status_dict.get('processed', 0) / total_leads * 100) if total_leads > 0 else 0.0

    return ConversionFunnelResponse(
        stages=stages,
        total_leads=total_leads,
        final_conversion_rate=round(final_conversion_rate, 2)
    )


@router.get("/channel-performance", response_model=ChannelPerformanceResponse)
async def get_channel_performance(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить производительность каналов.
    """
    # Дефолтные даты
    if not date_to:
        date_to = datetime.utcnow()
    if not date_from:
        date_from = date_to - timedelta(days=30)

    # Query для производительности каналов (только для подписок tenant'а)
    channel_stats = db.query(
        GlobalChannel.id,
        GlobalChannel.title,
        GlobalChannel.username,
        func.count(GlobalMessage.id).label('total_messages'),
        func.count(Lead.id).label('total_leads'),
        func.avg(Lead.score).label('avg_score'),
        func.max(GlobalMessage.created_at).label('last_message_date')
    ).join(
        ChannelSubscription,
        ChannelSubscription.channel_id == GlobalChannel.id
    ).outerjoin(
        GlobalMessage,
        GlobalMessage.channel_id == GlobalChannel.id
    ).outerjoin(
        Lead, and_(
            Lead.global_message_id == GlobalMessage.id,
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= date_from,
            Lead.created_at <= date_to
        )
    ).filter(
        ChannelSubscription.tenant_id == current_tenant.id
    ).group_by(GlobalChannel.id, GlobalChannel.title, GlobalChannel.username).all()

    channels = []
    for stat in channel_stats:
        total_messages = stat[3] or 0
        total_leads = stat[4] or 0
        conversion_rate = (total_leads / total_messages * 100) if total_messages > 0 else 0.0
        avg_score = float(stat[5]) if stat[5] else 0.0

        channels.append(ChannelPerformance(
            channel_id=str(stat[0]),
            channel_title=stat[1],
            channel_username=stat[2],
            total_messages=total_messages,
            total_leads=total_leads,
            conversion_rate=round(conversion_rate, 2),
            avg_lead_score=round(avg_score, 2),
            last_message_date=stat[6]
        ))

    # Сортируем по количеству лидов
    channels.sort(key=lambda x: x.total_leads, reverse=True)

    return ChannelPerformanceResponse(
        channels=channels,
        total_channels=len(channels)
    )


@router.get("/rule-performance", response_model=RulePerformanceResponse)
async def get_rule_performance(
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить производительность правил.
    """
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    # Query для производительности правил
    rule_stats = db.query(
        Rule.id,
        Rule.name,
        Rule.is_active,
        func.count(Lead.id).label('total_leads'),
        func.avg(Lead.score).label('avg_score'),
        func.sum(case((Lead.created_at >= seven_days_ago, 1), else_=0)).label('leads_7d'),
        func.sum(case((Lead.created_at >= thirty_days_ago, 1), else_=0)).label('leads_30d')
    ).outerjoin(Lead).filter(
        Rule.tenant_id == current_tenant.id
    ).group_by(Rule.id, Rule.name, Rule.is_active).all()

    rules = []
    for stat in rule_stats:
        rules.append(RulePerformance(
            rule_id=str(stat[0]),
            rule_name=stat[1],
            is_active=stat[2],
            total_leads=stat[3] or 0,
            avg_lead_score=round(float(stat[4]) if stat[4] else 0.0, 2),
            leads_last_7d=int(stat[5]) if stat[5] else 0,
            leads_last_30d=int(stat[6]) if stat[6] else 0
        ))

    # Сортируем по количеству лидов
    rules.sort(key=lambda x: x.total_leads, reverse=True)

    return RulePerformanceResponse(
        rules=rules,
        total_rules=len(rules)
    )


@router.get("/activity-trends", response_model=ActivityTrendsResponse)
async def get_activity_trends(
    current_tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Получить тренды активности (сравнение последних 7 дней с предыдущими 7 днями).
    """
    now = datetime.utcnow()
    current_period_start = now - timedelta(days=7)
    previous_period_start = now - timedelta(days=14)
    previous_period_end = current_period_start

    # Leads trend
    current_leads = db.query(func.count(Lead.id)).filter(
        and_(
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= current_period_start
        )
    ).scalar() or 0

    previous_leads = db.query(func.count(Lead.id)).filter(
        and_(
            Lead.tenant_id == current_tenant.id,
            Lead.created_at >= previous_period_start,
            Lead.created_at < previous_period_end
        )
    ).scalar() or 0

    leads_change = ((current_leads - previous_leads) / previous_leads * 100) if previous_leads > 0 else 0.0
    leads_direction = 'up' if leads_change > 5 else ('down' if leads_change < -5 else 'stable')

    # Messages trend (через subscriptions tenant'а)
    current_messages = db.query(func.count(GlobalMessage.id)).join(
        ChannelSubscription,
        ChannelSubscription.channel_id == GlobalMessage.channel_id
    ).filter(
        and_(
            ChannelSubscription.tenant_id == current_tenant.id,
            GlobalMessage.created_at >= current_period_start
        )
    ).scalar() or 0

    previous_messages = db.query(func.count(GlobalMessage.id)).join(
        ChannelSubscription,
        ChannelSubscription.channel_id == GlobalMessage.channel_id
    ).filter(
        and_(
            ChannelSubscription.tenant_id == current_tenant.id,
            GlobalMessage.created_at >= previous_period_start,
            GlobalMessage.created_at < previous_period_end
        )
    ).scalar() or 0

    messages_change = ((current_messages - previous_messages) / previous_messages * 100) if previous_messages > 0 else 0.0
    messages_direction = 'up' if messages_change > 5 else ('down' if messages_change < -5 else 'stable')

    # Conversion trend
    current_conversion = (current_leads / current_messages * 100) if current_messages > 0 else 0.0
    previous_conversion = (previous_leads / previous_messages * 100) if previous_messages > 0 else 0.0

    conversion_change = current_conversion - previous_conversion
    conversion_direction = 'up' if conversion_change > 1 else ('down' if conversion_change < -1 else 'stable')

    return ActivityTrendsResponse(
        leads_trend=ActivityTrend(
            metric_name="Leads Created",
            current_value=current_leads,
            previous_value=previous_leads,
            change_percentage=round(leads_change, 2),
            trend_direction=leads_direction
        ),
        messages_trend=ActivityTrend(
            metric_name="Messages Collected",
            current_value=current_messages,
            previous_value=previous_messages,
            change_percentage=round(messages_change, 2),
            trend_direction=messages_direction
        ),
        conversion_trend=ActivityTrend(
            metric_name="Conversion Rate",
            current_value=int(current_conversion),
            previous_value=int(previous_conversion),
            change_percentage=round(conversion_change, 2),
            trend_direction=conversion_direction
        ),
        period="Last 7 days vs Previous 7 days"
    )
