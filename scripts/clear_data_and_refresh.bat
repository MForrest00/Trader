docker-compose down
docker volume rm trader_redis_data trader_postgres_data
call .\scripts\run_services.bat
pipenv run python -c "from trader.models import initialize_models; initialize_models()"
pipenv run python -c "from trader.data.base import initialize_base_data; initialize_base_data()"
pipenv run python -c "from trader.data.country import update_countries_from_iso; update_countries_from_iso()"
pipenv run python -c "from trader.data.standard_currency import update_standard_currencies_from_iso; update_standard_currencies_from_iso()"
pipenv run python -c "from trader.data.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap; update_cryptocurrency_exchange_ranks_from_coin_market_cap()"
pipenv run python -c "from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap; update_current_cryptocurrency_ranks_from_coin_market_cap()"
