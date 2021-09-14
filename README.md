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

## Basic Process

1. Seed initial state (create records for various currencies, exchanges, and exchange markets)
1. Set initial enabled exchanges and quote currencies
1. Set up scheduled task to refresh strategy data
    1. Iterate through enabled base currencies (pair for enabled quote currency on an enabled exchange) and update OHLCV data
    1. Set a UUID and queue dependent data sources (e.g. Google trends) after each currency's OHLCV data is updated
    1. For
