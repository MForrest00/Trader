# Trader

## Commands

+ Tooling
  + `pipenv run black trader` - run `black` on `trader` module
  + `pipenv run pylint trader` - run `pylint` on `trader` module
+ Testing
  + `pipenv run coverage run -m pytest` - Run all tests with coverage
  + `pipenv run coverage run -m pytest -m integration` / `pipenv run coverage run -m pytest -m "not integration"` - Run all tests with coverage, targeting or excluding integration tests
  + `pipenv run coverage report` - Display coverage statistics from last run of tests with coverage
