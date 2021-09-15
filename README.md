# Trader

## Commands

+ Celery
  + `pipenv run celery -A trader.tasks beat` - run the `celery beat` service (only have one instance running at a time)
  + `pipenv run celery -A trader.tasks worker` - run a `celery` worker
  + `pipenv run celery -A trader.tasks flower` - run web based monitor and administration tool for `celery`
+ Tooling
  + `pipenv run black trader tests tools` - run `black` on `trader`, `tests`, and `tools` directories
  + `pipenv run pylint trader tests tools` - run `pylint` on `trader`, `tests`, and `tools` directories
+ Testing
  + `pipenv run coverage run -m pytest` - Run all tests with coverage
  + `pipenv run coverage run -m pytest -m integration` / `pipenv run coverage run -m pytest -m "not integration"` - Run all tests with coverage, targeting or excluding integration tests
  + `pipenv run coverage report` - Display coverage statistics from last run of tests with coverage
