docker-compose down
docker volume rm trader_redis_data trader_postgres_data trader_metabase_data
call .\scripts\run_development_services.bat
pipenv run python .\scripts\populate_initial_data.py
