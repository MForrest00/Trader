from datetime import timedelta
from typing import Set
from sqlalchemy.sql import func
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, ONE_DAY, STANDARD_CURRENCY
from trader.data.currency_ohlcv import update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap
from trader.models.cryptocurrency_exchange_market import CryptocurrencyExchangeMarket
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVPull
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.models.enabled_quote_currency import EnabledQuoteCurrency
from trader.tasks import app
from trader.utilities.functions import fetch_base_data_id, fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges


update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task = app.task(
    update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap
)


@app.task
def queue_update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task() -> None:
    with DBSession() as session:
        enabled_cryptocurrency_exchanges = (
            session.query(EnabledCryptocurrencyExchange).filter_by(is_disabled=False).all()
        )
        base_currency_ids = fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges(
            session, (e.cryptocurrency_exchange for e in enabled_cryptocurrency_exchanges)
        )
        coin_market_cap_id = fetch_base_data_id(COIN_MARKET_CAP)
        standard_currency_id = fetch_base_data_id(STANDARD_CURRENCY)
        one_day_id = fetch_base_data_id(ONE_DAY)
        us_dollar = session.query(Currency).filter_by(symbol="USD", currency_type_id=standard_currency_id).one()
        for base_currency_id in base_currency_ids:
            base_currency = session.query(Currency).get(base_currency_id)
            if base_currency:
                cryptocurrency = base_currency.cryptocurrency
                if cryptocurrency:
                    last_date = (
                        session.query(func.max(CurrencyOHLCV.date_open))
                        .select_from(CurrencyOHLCVPull)
                        .join(CurrencyOHLCV)
                        .filter(
                            CurrencyOHLCVPull.source_id == coin_market_cap_id,
                            CurrencyOHLCVPull.base_currency_id == base_currency.id,
                            CurrencyOHLCVPull.quote_currency_id == us_dollar.id,
                            CurrencyOHLCVPull.timeframe_id == one_day_id,
                        )
                        .one_or_none()
                    )
                    if last_date:
                        target_date = last_date[0] + timedelta(days=1)
                    else:
                        target_date = cryptocurrency.source_date_added
                    update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task.delay(cryptocurrency, target_date)
