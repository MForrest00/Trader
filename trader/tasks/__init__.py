from celery import Celery
from celery.schedules import crontab
from inflection import dasherize
from trader.utilities.environment import CELERY_REDIS_DATABASE, CELERY_REDIS_HOST, CELERY_REDIS_PORT


redis_endpoint = f"redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DATABASE}"
app = Celery(__name__, broker=redis_endpoint, backend=redis_endpoint)
app.conf.beat_schedule = {
    dasherize("update_countries_from_iso_task"): {
        "task": "trader.tasks.country.update_countries_from_iso_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize("update_standard_currencies_from_iso_task"): {
        "task": "trader.tasks.standard_currency.update_standard_currencies_from_iso_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize("update_cryptocurrency_exchange_ranks_from_coin_market_cap_task"): {
        "task": "trader.tasks.cryptocurrency_exchange_rank."
        + "update_cryptocurrency_exchange_ranks_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize("update_current_cryptocurrency_ranks_from_coin_market_cap_task"): {
        "task": "trader.tasks.cryptocurrency_rank.update_current_cryptocurrency_ranks_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize("queue_update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task"): {
        "task": "trader.tasks.currency_ohlcv.queue_update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=2),
    },
}
