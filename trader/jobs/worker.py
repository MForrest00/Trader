from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple
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


JOBS = (
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
