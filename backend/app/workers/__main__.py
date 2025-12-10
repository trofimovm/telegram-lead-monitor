"""
Standalone entry point for message collector worker.

This module serves as the main entry point when running the worker
as a separate process in Docker container.

Usage:
    python -m app.workers
"""
import asyncio
import signal
import sys
import logging

from app.workers import message_collector_worker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    signal_name = signal.Signals(sig).name
    logger.info(f"Received signal {signal_name}, initiating graceful shutdown...")
    shutdown_event.set()


async def main():
    """Main entry point for worker."""
    logger.info("=" * 60)
    logger.info("Starting Telegram Lead Monitor - Message Collector Worker")
    logger.info("=" * 60)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start the message collector worker V2
        # Interval: 1 minute (can be configured via environment variable)
        import os
        interval_minutes = int(os.getenv("WORKER_INTERVAL_MINUTES", "1"))

        logger.info(f"Collection interval: {interval_minutes} minutes")
        message_collector_worker.start(interval_minutes=interval_minutes)

        logger.info("Worker started successfully")
        logger.info("Press Ctrl+C to stop...")

        # Keep the worker running until shutdown signal
        await shutdown_event.wait()

    except Exception as e:
        logger.error(f"Fatal error in worker: {str(e)}", exc_info=True)
        sys.exit(1)

    finally:
        # Graceful shutdown
        logger.info("Shutting down worker...")
        message_collector_worker.stop()
        logger.info("Worker stopped gracefully")
        logger.info("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
        sys.exit(0)
