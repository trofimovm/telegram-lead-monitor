"""
Background worker V2 - использует глобальную архитектуру с progress tracking.
Эффективный сбор и анализ для масштабирования на тысячи пользователей.
"""
import logging
from datetime import datetime
from typing import Dict, Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.database import get_session_local
from app.services.global_message_collector import global_message_collector
from app.services.rule_processor_v2 import rule_processor_v2
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


class MessageCollectorWorkerV2:
    """
    Worker V2 для фонового сбора и анализа сообщений.

    Архитектура:
    1. Global Message Collection - собирает сообщения ОДИН раз для всех tenants
    2. Per-Tenant Rule Processing - анализирует только НОВЫЕ сообщения для каждого tenant
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False

    async def collect_and_analyze_job(self) -> Dict[str, Any]:
        """
        Главная задача: сбор глобальных сообщений + анализ для каждого tenant.

        Returns:
            Dict с полной статистикой выполнения
        """
        SessionLocal = get_session_local()
        db: Session = SessionLocal()
        start_time = datetime.utcnow()

        try:
            logger.info("="*80)
            logger.info("Starting Global Message Collection & Analysis Job V2...")
            logger.info("="*80)

            # ============================================================
            # ЭТАП 1: GLOBAL MESSAGE COLLECTION
            # Собираем сообщения из всех уникальных каналов (ОДИН раз!)
            # ============================================================
            logger.info("STAGE 1: Collecting global messages from channels...")

            collection_result = await global_message_collector.collect_global_messages(db)

            logger.info(
                f"Global collection complete: "
                f"processed {collection_result['channels_processed']} channels, "
                f"collected {collection_result['messages_collected']} new messages"
            )

            # ============================================================
            # ЭТАП 2: PER-TENANT RULE PROCESSING
            # Анализируем НОВЫЕ сообщения для каждого tenant
            # ============================================================
            logger.info("STAGE 2: Processing rules for all tenants...")

            # Получить всех активных tenants
            tenants = db.query(Tenant).filter(
                Tenant.deleted_at == None
            ).all()

            logger.info(f"Found {len(tenants)} active tenants to process")

            tenants_stats = []
            total_messages_analyzed = 0
            total_leads_created = 0
            all_lead_ids = []
            all_errors = collection_result.get('errors', [])

            for tenant in tenants:
                try:
                    logger.info(f"Processing tenant: {tenant.name} (ID: {tenant.id})")

                    tenant_result = await rule_processor_v2.process_rules_for_tenant(
                        tenant_id=tenant.id,
                        db=db
                    )

                    tenants_stats.append(tenant_result)
                    total_messages_analyzed += tenant_result['messages_analyzed']
                    total_leads_created += tenant_result['leads_created']
                    all_lead_ids.extend(tenant_result['lead_ids'])
                    all_errors.extend(tenant_result.get('errors', []))

                    logger.info(
                        f"Tenant {tenant.name}: "
                        f"analyzed {tenant_result['messages_analyzed']} messages, "
                        f"created {tenant_result['leads_created']} leads"
                    )

                except Exception as e:
                    error_msg = f"Error processing tenant {tenant.id}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    all_errors.append(error_msg)

            # ============================================================
            # ФИНАЛЬНАЯ СТАТИСТИКА
            # ============================================================
            duration = (datetime.utcnow() - start_time).total_seconds()

            logger.info("="*80)
            logger.info("JOB COMPLETED!")
            logger.info(f"Duration: {duration:.2f}s")
            logger.info(f"Global Messages Collected: {collection_result['messages_collected']}")
            logger.info(f"Tenants Processed: {len(tenants_stats)}")
            logger.info(f"Messages Analyzed: {total_messages_analyzed}")
            logger.info(f"Leads Created: {total_leads_created}")
            if all_errors:
                logger.warning(f"Errors: {len(all_errors)}")
            logger.info("="*80)

            return {
                # Global collection stats
                "channels_processed": collection_result['channels_processed'],
                "global_messages_collected": collection_result['messages_collected'],

                # Per-tenant analysis stats
                "tenants_processed": len(tenants_stats),
                "total_messages_analyzed": total_messages_analyzed,
                "total_leads_created": total_leads_created,
                "lead_ids": all_lead_ids,

                # Detailed stats
                "tenants_stats": tenants_stats,

                # Common
                "errors": all_errors,
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            logger.error(f"CRITICAL ERROR in collection job: {str(e)}", exc_info=True)

            return {
                "channels_processed": 0,
                "global_messages_collected": 0,
                "tenants_processed": 0,
                "total_messages_analyzed": 0,
                "total_leads_created": 0,
                "lead_ids": [],
                "tenants_stats": [],
                "errors": [str(e)],
                "duration_seconds": duration,
                "timestamp": datetime.utcnow().isoformat()
            }
        finally:
            db.close()

    def start(self, interval_minutes: int = 1):
        """
        Запустить worker с указанным интервалом.

        Args:
            interval_minutes: Интервал между запусками в минутах (по умолчанию 1)
        """
        if self.is_running:
            logger.warning("Message collector worker V2 is already running")
            return

        logger.info(f"Starting message collector worker V2 (interval: {interval_minutes} minutes)")

        # Добавляем задачу с интервальным триггером
        self.scheduler.add_job(
            self.collect_and_analyze_job,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id="collect_and_analyze_v2",
            name="Global Message Collection & Analysis V2",
            replace_existing=True,
            max_instances=1,  # Не запускать параллельно
        )

        self.scheduler.start()
        self.is_running = True
        logger.info("Message collector worker V2 started successfully")

    def stop(self):
        """Остановить worker."""
        if not self.is_running:
            return

        logger.info("Stopping message collector worker V2...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("Message collector worker V2 stopped")

    async def run_once(self) -> Dict[str, Any]:
        """
        Выполнить однократный сбор и анализ (для тестирования или ручного запуска).

        Returns:
            Dict с результатами выполнения
        """
        logger.info("Running manual global collection and analysis...")
        return await self.collect_and_analyze_job()


# Глобальный экземпляр worker V2
message_collector_worker_v2 = MessageCollectorWorkerV2()
