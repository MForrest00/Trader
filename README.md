# Trader

## Commands

+ Celery
  + `pipenv run celery -A trader.tasks beat` - run the `celery beat` service (only have one instance running at a time)
  + `pipenv run celery -A trader.tasks worker` - run a `celery` worker
+ Tooling
  + `pipenv run black trader tests scripts` - run `black` on `trader`, `tests`, and `scripts` directories
  + `pipenv run pylint trader tests scripts` - run `pylint` on `trader`, `tests`, and `scripts` directories
+ Testing
  + `pipenv run coverage run -m pytest` - Run all tests with coverage
  + `pipenv run coverage run -m pytest -m integration` / `pipenv run coverage run -m pytest -m "not integration"` - Run all tests with coverage, targeting or excluding integration tests
  + `pipenv run coverage report` - Display coverage statistics from last run of tests with coverage

## TODOs

+ Possible rename many-to-many assocation tables (plural forms of each side? xref?)
