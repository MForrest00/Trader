docker-compose down
docker volume rm trader_redis_data trader_postgres_data
call .\scripts\run_services.bat
pipenv run python -c "from trader.models import initialize_models; initialize_models()"
pipenv run python -c "from trader.data.base import initialize_base_data; initialize_base_data()"
pipenv run python -c "from trader.data.country import update_country_data_from_iso; update_country_data_from_iso()"
pipenv run python -c "from trader.data.currency import update_currency_data_from_iso; update_currency_data_from_iso()"
