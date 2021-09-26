from celery import Celery
from celery.schedules import crontab
from inflection import dasherize
from trader.utilities.environment import CELERY_REDIS_DATABASE, CELERY_REDIS_HOST, CELERY_REDIS_PORT


redis_endpoint = f"redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DATABASE}"
app = Celery(__name__, broker=redis_endpoint, backend=redis_endpoint)
app.conf.broker_transport_options = {
    "priority_steps": list(range(5)),
    "sep": ":",
    "queue_order_strategy": "priority",
}
app.conf.beat_schedule = {
    dasherize("update_countries_from_iso_task"): {
        "task": "trader.tasks.country.update_countries_from_iso_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("update_standard_currencies_from_iso_task"): {
        "task": "trader.tasks.standard_currency.update_standard_currencies_from_iso_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("update_cryptocurrency_exchange_ranks_from_coin_market_cap_task"): {
        "task": "trader.tasks.cryptocurrency_exchange_rank."
        + "update_cryptocurrency_exchange_ranks_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("update_current_cryptocurrency_ranks_from_coin_market_cap_task"): {
        "task": "trader.tasks.cryptocurrency_rank.update_current_cryptocurrency_ranks_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task"): {
        "task": "trader.tasks.asset_ohlcv.queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=2),
        "options": {
            "priority": 4,
        },
    },
}


from trader.tasks.asset_ohlcv import (
    queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task,
    update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap_task,
)
from trader.tasks.country import update_countries_from_iso_task
from trader.tasks.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap_task
from trader.tasks.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap_task
from trader.tasks.standard_currency import update_standard_currencies_from_iso_task
