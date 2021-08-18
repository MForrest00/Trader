docker-compose down
docker volume rm trader_redis_data trader_postgres_data
call .\scripts\run_services.bat
pipenv run python -c "from trader.persistence.models import initialize_models; initialize_models()"
pipenv run python -c "from trader.persistence.base_data import initialize_base_data; initialize_base_data()"
pipenv run python -c "from trader.data.currency import update_iso_currency_codes; update_iso_currency_codes()"
