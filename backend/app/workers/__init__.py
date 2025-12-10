# Import V2 worker (with global architecture)
from app.workers.message_collector_v2 import message_collector_worker_v2 as message_collector_worker

__all__ = ["message_collector_worker"]
