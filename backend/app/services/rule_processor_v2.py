"""
Rule Processor V2 - обработка правил с использованием global_messages и progress tracking.
Эффективная архитектура для масштабирования на тысячи пользователей.
"""
import logging
from typing import Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from app.models.global_channel import GlobalChannel
from app.models.global_message import GlobalMessage
from app.models.channel_subscription import ChannelSubscription
from app.models.rule import Rule
from app.models.rule_analysis_progress import RuleAnalysisProgress
from app.models.lead import Lead
from app.models.user import User
from app.services.llm_service import llm_service
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class RuleProcessorV2:
    """
    Процессор правил V2 с эффективным progress tracking.
    - Использует global_messages вместо tenant-specific messages
    - Отслеживает прогресс через last_analyzed_message_id
    - Анализирует только НОВЫЕ сообщения
    """

    async def process_rules_for_tenant(
        self,
        tenant_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Обрабатывает все правила одного tenant.

        Args:
            tenant_id: UUID tenant'а
            db: Database session

        Returns:
            Dict со статистикой:
            {
                "tenant_id": str,
                "rules_processed": int,
                "messages_analyzed": int,
                "leads_created": int,
                "lead_ids": List[UUID],
                "errors": List[str]
            }
        """
        stats = {
            "tenant_id": str(tenant_id),
            "rules_processed": 0,
            "messages_analyzed": 0,
            "leads_created": 0,
            "lead_ids": [],
            "errors": []
        }

        # Получить все активные правила tenant'а
        rules = db.query(Rule).filter(
            Rule.tenant_id == tenant_id,
            Rule.is_active == True
        ).all()

        if not rules:
            logger.debug(f"No active rules for tenant {tenant_id}")
            return stats

        logger.info(f"Processing {len(rules)} rules for tenant {tenant_id}")

        for rule in rules:
            try:
                result = await self._process_rule(
                    rule=rule,
                    tenant_id=tenant_id,
                    db=db
                )

                stats["rules_processed"] += 1
                stats["messages_analyzed"] += result["messages_analyzed"]
                stats["leads_created"] += result["leads_created"]
                stats["lead_ids"].extend(result["lead_ids"])

            except Exception as e:
                error_msg = f"Error processing rule {rule.id}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                stats["errors"].append(error_msg)

        logger.info(
            f"Tenant {tenant_id} processing complete: "
            f"analyzed {stats['messages_analyzed']} messages, "
            f"created {stats['leads_created']} leads"
        )

        return stats

    async def _process_rule(
        self,
        rule: Rule,
        tenant_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Обрабатывает одно правило для tenant'а.

        Returns:
            {
                "rule_id": UUID,
                "messages_analyzed": int,
                "leads_created": int,
                "lead_ids": List[UUID]
            }
        """
        stats = {
            "rule_id": str(rule.id),
            "messages_analyzed": 0,
            "leads_created": 0,
            "lead_ids": []
        }

        # Получить подписки tenant'а на каналы
        subscriptions = db.query(ChannelSubscription).filter(
            ChannelSubscription.tenant_id == tenant_id,
            ChannelSubscription.is_active == True
        ).all()

        if not subscriptions:
            logger.debug(f"No active subscriptions for tenant {tenant_id}")
            return stats

        # Определяем, какие каналы обрабатывать для этого правила
        if rule.channel_ids:
            # Правило применяется только к указанным каналам
            channels_to_process = rule.channel_ids
            logger.debug(f"Rule {rule.id}: will process {len(channels_to_process)} specific channels")
        else:
            # channel_ids = NULL означает "все подписанные каналы"
            channels_to_process = None
            logger.debug(f"Rule {rule.id}: will process all subscribed channels")

        # Обработать каждую подписку (канал)
        for subscription in subscriptions:
            channel = subscription.channel

            # Фильтруем каналы по channel_ids правила
            if channels_to_process is not None and channel.id not in channels_to_process:
                logger.debug(f"Skipping channel {channel.id} - not in rule.channel_ids")
                continue

            try:
                # Получить прогресс анализа для этого (rule, channel)
                progress = db.query(RuleAnalysisProgress).filter(
                    RuleAnalysisProgress.rule_id == rule.id,
                    RuleAnalysisProgress.channel_id == channel.id
                ).first()

                # Получить НОВЫЕ сообщения из канала (которые еще не анализировали)
                query = db.query(GlobalMessage).filter(
                    GlobalMessage.channel_id == channel.id
                )

                if progress and progress.last_analyzed_message_id:
                    # Инкрементальный режим: берем сообщения ПОСЛЕ последнего
                    last_msg = db.query(GlobalMessage).get(progress.last_analyzed_message_id)
                    if last_msg:
                        query = query.filter(
                            GlobalMessage.sent_at > last_msg.sent_at
                        )
                else:
                    # Новый канал для правила: анализируем историю
                    # Ограничение: последние 5 дней
                    five_days_ago = datetime.utcnow() - timedelta(days=5)
                    query = query.filter(
                        GlobalMessage.sent_at >= five_days_ago
                    )
                    logger.info(
                        f"New rule-channel pair: analyzing history from last 5 days for "
                        f"rule {rule.id}, channel {channel.id}"
                    )

                # Сортировка по sent_at ASC, максимум 100 сообщений за раз
                new_messages = query.order_by(
                    GlobalMessage.sent_at.asc()
                ).limit(100).all()

                if not new_messages:
                    continue  # Нет новых сообщений для этого канала

                logger.info(
                    f"Rule {rule.id} / Channel {channel.username or channel.tg_id}: "
                    f"processing {len(new_messages)} new messages"
                )

                # Анализировать каждое новое сообщение
                for message in new_messages:
                    try:
                        # Проверить: уже есть лид?
                        existing_lead = db.query(Lead).filter(
                            Lead.tenant_id == tenant_id,
                            Lead.global_message_id == message.id,
                            Lead.rule_id == rule.id
                        ).first()

                        if existing_lead:
                            # Лид уже создан (race condition или повторный запуск)
                            logger.debug(f"Lead already exists for message {message.id} and rule {rule.id}")

                            # Обновляем progress даже если лид существует
                            self._update_progress(
                                rule_id=rule.id,
                                channel_id=channel.id,
                                last_analyzed_message_id=message.id,
                                lead_created=False,
                                db=db,
                                progress=progress
                            )
                            continue

                        # Проверить что сообщение имеет текст
                        if not message.text:
                            # Обновляем progress но не создаем лид
                            self._update_progress(
                                rule_id=rule.id,
                                channel_id=channel.id,
                                last_analyzed_message_id=message.id,
                                lead_created=False,
                                db=db,
                                progress=progress
                            )
                            continue

                        stats["messages_analyzed"] += 1

                        # Анализировать через LLM
                        analysis = await llm_service.analyze_message(
                            message_text=message.text,
                            rule_description=rule.prompt
                        )

                        # Если match и превышает threshold - создать лид
                        if analysis["is_match"] and analysis["confidence"] >= float(rule.threshold):
                            lead = await self._create_lead(
                                tenant_id=tenant_id,
                                global_message=message,
                                rule=rule,
                                analysis=analysis,
                                db=db
                            )

                            stats["leads_created"] += 1
                            stats["lead_ids"].append(lead.id)

                            logger.info(
                                f"Lead created: global_message_id={message.id}, "
                                f"rule_id={rule.id}, score={lead.score}"
                            )

                            # Обновить прогресс (с лидом)
                            self._update_progress(
                                rule_id=rule.id,
                                channel_id=channel.id,
                                last_analyzed_message_id=message.id,
                                lead_created=True,
                                db=db,
                                progress=progress
                            )
                        else:
                            logger.debug(
                                f"Message {message.id} does not match rule {rule.id}: "
                                f"is_match={analysis['is_match']}, confidence={analysis['confidence']}"
                            )

                            # Обновить прогресс (без лида)
                            self._update_progress(
                                rule_id=rule.id,
                                channel_id=channel.id,
                                last_analyzed_message_id=message.id,
                                lead_created=False,
                                db=db,
                                progress=progress
                            )

                    except Exception as e:
                        logger.error(
                            f"Error analyzing message {message.id} with rule {rule.id}: {str(e)}",
                            exc_info=True
                        )
                        # Продолжаем со следующим сообщением

            except Exception as e:
                logger.error(
                    f"Error processing channel {channel.id} for rule {rule.id}: {str(e)}",
                    exc_info=True
                )
                # Продолжаем со следующим каналом

        return stats

    def _update_progress(
        self,
        rule_id: str,
        channel_id: str,
        last_analyzed_message_id: str,
        lead_created: bool,
        db: Session,
        progress: RuleAnalysisProgress = None
    ):
        """
        Обновляет прогресс анализа для пары (rule, channel).
        """
        if not progress:
            # Создать новый progress
            progress = RuleAnalysisProgress(
                rule_id=rule_id,
                channel_id=channel_id,
                last_analyzed_message_id=last_analyzed_message_id,
                last_analyzed_at=datetime.utcnow(),
                messages_analyzed=1,
                leads_created=1 if lead_created else 0
            )
            db.add(progress)
        else:
            # Обновить существующий
            progress.last_analyzed_message_id = last_analyzed_message_id
            progress.last_analyzed_at = datetime.utcnow()
            progress.messages_analyzed += 1
            if lead_created:
                progress.leads_created += 1

        db.commit()

    async def _create_lead(
        self,
        tenant_id: str,
        global_message: GlobalMessage,
        rule: Rule,
        analysis: Dict[str, Any],
        db: Session
    ) -> Lead:
        """
        Создает лид на основе анализа глобального сообщения.

        Args:
            tenant_id: UUID tenant'а
            global_message: Глобальное сообщение
            rule: Правило, которое сработало
            analysis: Результат LLM анализа
            db: Database session

        Returns:
            Lead: Созданный лид
        """
        # Извлекаем сущности из сообщения
        try:
            extracted_entities = await llm_service.extract_entities(global_message.text)
        except Exception as e:
            logger.warning(f"Failed to extract entities: {str(e)}")
            extracted_entities = {
                "contacts": [],
                "keywords": [],
                "budget": None,
                "deadline": None,
                "summary": global_message.text[:200] + "..." if len(global_message.text) > 200 else global_message.text
            }

        # Создаем лид с global_message_id
        lead = Lead(
            tenant_id=tenant_id,
            global_message_id=global_message.id,
            rule_id=rule.id,
            score=Decimal(str(analysis["confidence"])),
            reasoning=analysis["reasoning"],
            extracted_entities=extracted_entities,
            status="new"
        )

        db.add(lead)
        db.commit()
        db.refresh(lead)

        # Загружаем связанные объекты для уведомления
        lead = db.query(Lead).options(
            joinedload(Lead.rule),
            joinedload(Lead.global_message).joinedload(GlobalMessage.channel)
        ).filter(Lead.id == lead.id).first()

        # Получаем пользователя (владельца tenant)
        user = db.query(User).filter(User.tenant_id == tenant_id).first()

        # Создаем уведомление о новом лиде
        if user:
            try:
                await notification_service.create_new_lead_notification(
                    db=db,
                    lead=lead,
                    user=user
                )
                logger.info(f"Notification sent for lead {lead.id} to user {user.id}")
            except Exception as e:
                logger.error(f"Failed to create notification for lead {lead.id}: {str(e)}", exc_info=True)
        else:
            logger.warning(f"No user found for tenant {tenant_id}, notification not sent for lead {lead.id}")

        return lead


# Глобальный экземпляр процессора V2
rule_processor_v2 = RuleProcessorV2()
