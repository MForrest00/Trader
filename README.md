# Trader

## Environment Variables

+ `CACHE_REDIS_HOST` - host for cache Redis instance
+ `CACHE_REDIS_PORT` - port for cache Redis instance
+ `CACHE_REDIS_DATABASE` - database for cache Redis instance
+ `CELERY_REDIS_HOST` - host for celery Redis instance
+ `CELERY_REDIS_PORT` - port for celery Redis instance
+ `CELERY_REDIS_DATABASE` - database for celery Redis instance
+ `POSTGRES_USER` - user for Postgres database
+ `POSTGRES_PASSWORD` - password for Postgres database
+ `POSTGRES_HOST` - host for Postgres database
+ `POSTGRES_PORT` - port for Postgres database
+ `POSTGRES_DATABASE` - database for Postgres database
+ `REMOTE_WEBDRIVER_HOST` - host for remote selenium server
+ `REMOTE_WEBDRIVER_PORT` - port for remote selenium server

## Commands

+ Celery
  + `pipenv run celery -A trader.tasks beat` - run the `celery beat` service (only have one instance running at a time)
  + `pipenv run celery -A trader.tasks worker` - run a `celery` worker
  + `pipenv run celery -A trader.tasks flower` - run web based monitor and administration tool for `celery`
+ Tooling
  + `pipenv run black trader tests tools` - run `black` on `trader`, `tests`, and `tools` directories
  + `pipenv run pylint trader tests tools` - run `pylint` on `trader`, `tests`, and `tools` directories
  + `pipenv run vulture` - run `vulture`
+ Testing
  + `pipenv run coverage run -m pytest` - Run all tests with coverage
  + `pipenv run coverage run -m pytest -m integration` / `pipenv run coverage run -m pytest -m "not integration"` - Run all tests with coverage, targeting or excluding integration tests
  + `pipenv run coverage report` - Display coverage statistics from last run of tests with coverage

## Data Feed Refresh Process

+ Data feed refreshes are kicked off via celery beat tasks
+ If a refresh of a particular data feed results in new records written to the database, two tasks need to be performed: 1. the new data needs to be processed by entry strategies to find buy signals, and 2. the new data needs to be processed by exit strategies for existing positions to find sell signals
+ If a buy signal is generated, the resulting buy signal needs to be processed by individual users to possibly create positions

## TODOs

+ Maybe try to handle duplicate queued tasks (<https://stackoverflow.com/questions/26831103/avoiding-duplicate-tasks-in-celery-broker>)
