cd /d %~dp0
cd ..
docker-compose down
docker volume rm trader_redis_data trader_postgres_data
.\scripts\run_services.bat
pipenv run python -c "from trader.persistence.models import initialize_models; initialize_models()"
pipenv run python -c "from trader.persistence.base_data import initialize_base_data; initialize_base_data()"
