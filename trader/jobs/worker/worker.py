from dataclasses import dataclass
from typing import Any, Callable, Dict, Set, Tuple
from rq import Queue
from rq.registry import ScheduledJobRegistry, StartedJobRegistry
from trader.connections.queue import data_retrieval_queue
from trader.jobs import JobData
from trader.jobs.country import update_countries, update_countries_data
from trader.jobs.cryptocurrency_ranks import (
    update_current_cryptocurrency_ranks,
    update_current_cryptocurrency_ranks_data,
)
from trader.jobs.standard_currency import update_standard_currencies, update_standard_currencies_data


@dataclass
class WorkerJob:
    job_data: JobData
    function: Callable
    args: Tuple = ()
    kwargs: Dict[str, Any] = {}


DATA_RETRIEVAL_JOBS = (
    WorkerJob(
        job_data=update_countries_data,
        function=update_countries,
    ),
    WorkerJob(
        job_data=update_standard_currencies_data,
        function=update_standard_currencies,
    ),
    WorkerJob(
        job_data=update_current_cryptocurrency_ranks_data,
        function=update_current_cryptocurrency_ranks,
    ),
)


def remove_iteration_suffix(job_id: str) -> str:
    return "_".join(job_id.split("_")[:-1])


def get_queued_started_scheduled_job_ids_for_queue(queue: Queue) -> Set[str]:
    started_registry = StartedJobRegistry(queue=queue)
    scheduled_registry = ScheduledJobRegistry(queue=queue)
    return (
        {remove_iteration_suffix(j) for j in scheduled_registry.get_job_ids()}
        | {remove_iteration_suffix(j) for j in queue.job_ids}
        | {remove_iteration_suffix(j) for j in started_registry.get_job_ids()}
    )


def check_jobs() -> None:
    data_retrieval_job_ids = get_queued_started_scheduled_job_ids_for_queue(data_retrieval_queue)
    for job in DATA_RETRIEVAL_JOBS:
        if job.job_data.job_id not in data_retrieval_job_ids:
            current_run = job.job_data.current_run()
            if current_run is True:
                data_retrieval_queue.enqueue(
                    job.function,
                    job_id=f"{job.job_data.job_id}_0",
                    result_ttl=job.job_data.result_ttl,
                    args=(job.job_data, *job.args),
                    kwargs=job.kwargs,
                )
            else:
                data_retrieval_queue.enqueue_at(
                    current_run,
                    job.function,
                    job_id=f"{job.job_data.job_id}_0",
                    result_ttl=job.job_data.result_ttl,
                    args=(job.job_data, *job.args),
                    kwargs=job.kwargs,
                )
