call .\tools\stop_development_services.bat
docker volume rm trader_redis_data trader_postgres_data trader_metabase_data
call .\tools\start_development_services.bat
pipenv run python .\tools\populate_initial_data.py
