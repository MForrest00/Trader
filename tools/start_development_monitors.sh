#!/bin/bash
docker-compose -f docker-compose.yml -f docker-compose.development.yml up -d celery_beat data_feed_monitor
