from trader.data.standard_currency import update_standard_currencies_from_iso
from trader.tasks import app


update_standard_currencies_from_iso_task = app.task(update_standard_currencies_from_iso)
