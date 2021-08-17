from rq.exceptions import NoSuchJobError
from rq.job import Job
from trader.connections.cache import cache
from trader.worker.jobs import JOBS


def main():
    for job in JOBS:
        try:
            queued_job = Job.fetch(job.job_data.job_id, connection=cache)
        except NoSuchJobError:
            pass
        job_status = queued_job.get_status()


if __name__ == "__main__":
    main()
