from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Tuple
from rq import Queue
from trader.connections.queue import data_retrieval_queue
from trader.data.cryptocurrency.top_cryptocurrency import update_top_cryptocurrencies_from_coin_market_cap


@dataclass
class JobData:
    job_id: str
    target_queue: Queue
    result_ttl: int = 0


update_top_cryptocurrencies_data = JobData(
    job_id="update_top_cryptocurrencies",
    target_queue=data_retrieval_queue,
)


def update_top_cryptocurrencies():
    update_top_cryptocurrencies_from_coin_market_cap()
    update_top_cryptocurrencies_data.target_queue.enqueue_at(
        datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
        update_top_cryptocurrencies,
        job_id=update_top_cryptocurrencies_data.job_id,
        result_ttl=update_top_cryptocurrencies_data.result_ttl,
    )


@dataclass
class WorkerJob:
    job_data: JobData
    function: Callable
    args: Tuple = ()
    kwargs: Dict[str, Any] = {}


JOBS = (
    WorkerJob(
        job_data=update_top_cryptocurrencies_data,
        function=update_top_cryptocurrencies_from_coin_market_cap,
    ),
)
