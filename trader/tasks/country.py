from trader.data.country import update_countries_from_iso
from trader.tasks import app


update_countries_from_iso_task = app.task(update_countries_from_iso)
