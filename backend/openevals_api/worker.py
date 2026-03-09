from __future__ import annotations

import dramatiq
from dramatiq.brokers.redis import RedisBroker

from openevals_api.config import get_settings
from openevals_api.database import SessionLocal, init_db
from openevals_api.services.runs import process_run_by_id

settings = get_settings()
broker = RedisBroker(url=settings.redis_url)
dramatiq.set_broker(broker)


def process_run(run_id: str) -> None:
    process_run_by_id(run_id)


@dramatiq.actor(queue_name="evals")
def run_eval(run_id: str) -> None:
    process_run(run_id)


def enqueue_run(run_id: str) -> None:
    if settings.inline_runs:
        process_run(run_id)
    else:
        run_eval.send(run_id)


def main() -> None:
    init_db()
    from dramatiq.cli import main as dramatiq_main

    dramatiq_main(["openevals_api.worker"])
