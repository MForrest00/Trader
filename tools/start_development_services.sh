#!/bin/bash
docker-compose -f docker-compose.yml -f docker-compose.development.yml up -d redis postgres metabase pgadmin celery_beat celery_worker
