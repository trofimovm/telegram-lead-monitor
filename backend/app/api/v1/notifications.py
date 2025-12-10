"""
API endpoints для работы с уведомлениями.
Включает: список уведомлений, статистику, пометку как прочитанное, удаление.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.api.deps import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationMarkAsRead,
    NotificationMarkAllAsRead,
    NotificationStats,
)
from app.api.deps import get_current_active_user as get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    is_read: Optional[bool] = Query(None, description="Фильтр по прочитанным/непрочитанным"),
    notification_type: Optional[NotificationType] = Query(None, description="Фильтр по типу"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список уведомлений текущего пользователя.

    Поддерживает фильтрацию по прочитанным/непрочитанным и по типу.
    """
    # Базовый query
    query = db.query(Notification).filter(Notification.tenant_id == current_user.id)

    # Применить фильтры
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    if notification_type:
        query = query.filter(Notification.type == notification_type)

    # Получить total count
    total = query.count()

    # Получить unread count
    unread_count = db.query(Notification).filter(
        and_(
            Notification.tenant_id == current_user.id,
            Notification.is_read == False
        )
    ).count()

    # Получить уведомления с пагинацией (сортировка по дате создания, новые первые)
    notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

    return NotificationListResponse(
        notifications=notifications,
        total=total,
        unread_count=unread_count,
    )


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить статистику по уведомлениям текущего пользователя.
    """
    # Total count
    total = db.query(Notification).filter(Notification.tenant_id == current_user.id).count()

    # Unread count
    unread = db.query(Notification).filter(
        and_(
            Notification.tenant_id == current_user.id,
            Notification.is_read == False
        )
    ).count()

    # By type
    by_type_query = db.query(
        Notification.type,
        func.count(Notification.id).label("count")
    ).filter(
        Notification.tenant_id == current_user.id
    ).group_by(Notification.type).all()

    by_type = {notification_type: count for notification_type, count in by_type_query}

    # Ensure all types are present (with 0 if no notifications)
    for nt in NotificationType:
        if nt not in by_type:
            by_type[nt] = 0

    # Recent count (last 24 hours)
    cutoff = datetime.utcnow() - timedelta(hours=24)
    recent_count = db.query(Notification).filter(
        and_(
            Notification.tenant_id == current_user.id,
            Notification.created_at >= cutoff
        )
    ).count()

    return NotificationStats(
        total=total,
        unread=unread,
        by_type=by_type,
        recent_count=recent_count,
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить одно уведомление по ID.
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.tenant_id == current_user.id
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    data: NotificationMarkAsRead,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Пометить уведомление как прочитанное/непрочитанное.
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.tenant_id == current_user.id
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    # Обновить статус
    notification.is_read = data.is_read
    if data.is_read and not notification.read_at:
        notification.read_at = datetime.utcnow()
    elif not data.is_read:
        notification.read_at = None

    db.commit()
    db.refresh(notification)

    return notification


@router.post("/mark-all-read", response_model=NotificationMarkAllAsRead)
async def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Пометить все уведомления как прочитанные.
    """
    # Обновить все непрочитанные уведомления
    updated_count = db.query(Notification).filter(
        and_(
            Notification.tenant_id == current_user.id,
            Notification.is_read == False
        )
    ).update(
        {
            Notification.is_read: True,
            Notification.read_at: datetime.utcnow()
        },
        synchronize_session=False
    )

    db.commit()

    return NotificationMarkAllAsRead(marked_count=updated_count)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить уведомление.
    """
    notification = db.query(Notification).filter(
        and_(
            Notification.id == notification_id,
            Notification.tenant_id == current_user.id
        )
    ).first()

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    db.delete(notification)
    db.commit()

    return None
