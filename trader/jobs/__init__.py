from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Union
from rq import Queue


def bind_self(function: Callable) -> Callable:
    return function.__get__(function, type(function))


@dataclass
class JobData:
    job_id: str
    current_run: Callable[[], Union[bool, datetime]]
    next_run: Callable[[], datetime]
    target_queue: Queue
    result_ttl: int = 0
