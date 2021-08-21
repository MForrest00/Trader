from datetime import datetime, timedelta
from typing import Callable
from trader.connections.queue import data_retrieval_queue
from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.jobs import bind_self, JobData


update_standard_currencies_data = JobData(
    job_id="update_standard_currencies",
    current_run=lambda: True,
    next_run=lambda: datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7),
    target_queue=data_retrieval_queue,
)


@bind_self
def update_standard_currencies(self: Callable) -> None:
    update_standard_currencies_from_iso()
    update_standard_currencies_data.target_queue.enqueue_at(
        update_standard_currencies_data.next_run,
        self,
        job_id=update_standard_currencies_data.job_id,
        result_ttl=update_standard_currencies_data.result_ttl,
    )
