from celery import Celery
from celery.schedules import crontab
from inflection import dasherize
from trader.data.country import update_countries_from_iso
from trader.data.cryptocurrency_exchange_rank import update_cryptocurrency_exchange_ranks_from_coin_market_cap
from trader.data.cryptocurrency_rank import update_current_cryptocurrency_ranks_from_coin_market_cap
from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.utilities.environment import CELERY_REDIS_DATABASE, CELERY_REDIS_HOST, CELERY_REDIS_PORT


redis_endpoint = f"redis://{CELERY_REDIS_HOST}:{CELERY_REDIS_PORT}/{CELERY_REDIS_DATABASE}"
app = Celery(__name__, broker=redis_endpoint, backend=redis_endpoint)


update_countries_from_iso_task = app.task(update_countries_from_iso)
update_standard_currencies_from_iso_task = app.task(update_standard_currencies_from_iso)
update_cryptocurrency_exchange_ranks_from_coin_market_cap_task = app.task(
    update_cryptocurrency_exchange_ranks_from_coin_market_cap
)
update_current_cryptocurrency_ranks_from_coin_market_cap_task = app.task(
    update_current_cryptocurrency_ranks_from_coin_market_cap
)


app.conf.beat_schedule = {
    dasherize(update_countries_from_iso_task.__name__): {
        "task": "trader.tasks.update_countries_from_iso_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize(update_standard_currencies_from_iso_task.__name__): {
        "task": "trader.tasks.update_standard_currencies_from_iso_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize(update_cryptocurrency_exchange_ranks_from_coin_market_cap_task.__name__): {
        "task": "trader.tasks.update_cryptocurrency_exchange_ranks_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=0, day_of_week="mon"),
    },
    dasherize(update_current_cryptocurrency_ranks_from_coin_market_cap_task.__name__): {
        "task": "trader.tasks.update_current_cryptocurrency_ranks_from_coin_market_cap_task",
        "schedule": crontab(minute=0, hour=0),
    },
}
