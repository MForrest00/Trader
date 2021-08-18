from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Tuple
from rq import Queue
from trader.connections.queue import data_retrieval_queue
from trader.data.cryptocurrency.cryptocurrency_rank import update_cryptocurrency_ranks_from_coin_market_cap


@dataclass
class JobData:
    job_id: str
    target_queue: Queue
    result_ttl: int = 0


update_cryptocurrency_ranks_data = JobData(
    job_id="update_cryptocurrency_ranks",
    target_queue=data_retrieval_queue,
)


def update_cryptocurrency_ranks():
    update_cryptocurrency_ranks_from_coin_market_cap()
    update_cryptocurrency_ranks_data.target_queue.enqueue_at(
        datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
        update_cryptocurrency_ranks,
        job_id=update_cryptocurrency_ranks_data.job_id,
        result_ttl=update_cryptocurrency_ranks_data.result_ttl,
    )


@dataclass
class WorkerJob:
    job_data: JobData
    function: Callable
    args: Tuple = ()
    kwargs: Dict[str, Any] = {}


JOBS = (
    WorkerJob(
        job_data=update_cryptocurrency_ranks_data,
        function=update_cryptocurrency_ranks_from_coin_market_cap,
    ),
)
