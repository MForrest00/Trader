from datetime import datetime, timedelta
from typing import Callable
from trader.connections.queue import data_retrieval_queue
from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.jobs import bind_self, JobData


update_current_cryptocurrency_ranks_data = JobData(
    job_id="update_current_cryptocurrency_ranks",
    current_run=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
    next_run=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
    target_queue=data_retrieval_queue,
)


@bind_self
def update_current_cryptocurrency_ranks(self: Callable) -> None:
    update_current_cryptocurrency_ranks_from_coin_market_cap()
    update_current_cryptocurrency_ranks_data.target_queue.enqueue_at(
        update_current_cryptocurrency_ranks_data.next_run,
        self,
        job_id=update_current_cryptocurrency_ranks_data.job_id,
        result_ttl=update_current_cryptocurrency_ranks_data.result_ttl,
    )
