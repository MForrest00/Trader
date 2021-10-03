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
app.conf.task_ignore_result = True
app.conf.task_time_limit = 60 * 10
app.conf.beat_schedule = {
    dasherize("update_countries_from_iso"): {
        "task": "trader.tasks.country.update_countries_from_iso",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("update_standard_currencies_from_iso"): {
        "task": "trader.tasks.standard_currency.update_standard_currencies_from_iso",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("update_cryptocurrency_exchange_ranks_from_coin_market_cap"): {
        "task": "trader.tasks.cryptocurrency_exchange_rank.update_cryptocurrency_exchange_ranks_from_coin_market_cap",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("update_current_cryptocurrency_ranks_from_coin_market_cap"): {
        "task": "trader.tasks.cryptocurrency_rank.update_current_cryptocurrency_ranks_from_coin_market_cap",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("queue_update_cryptocurrency_exchange_market_stats_from_coin_market_cap"): {
        "task": "trader.tasks.cryptocurrency_exchange_market_stat"
        + ".queue_update_cryptocurrency_exchange_market_stats_from_coin_market_cap",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
        "options": {
            "priority": 1,
        },
    },
    dasherize("queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap"): {
        "task": "trader.tasks.asset_ohlcv.queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap",
        "schedule": crontab(minute=0, hour=2),
        "options": {
            "priority": 4,
        },
    },
}


from trader.tasks.asset_ohlcv import (
    queue_update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap,
    update_cryptocurrency_one_day_asset_ohlcv_from_coin_market_cap,
)
from trader.tasks.country import update_countries_from_iso
from trader.tasks.cryptocurrency_exchange_market_stat import (
    queue_update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
    update_cryptocurrency_exchange_market_stats_from_coin_market_cap,
)
from trader.tasks.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.tasks.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.tasks.implementation import run_implementations
from trader.tasks.standard_currency import update_standard_currencies_from_iso
