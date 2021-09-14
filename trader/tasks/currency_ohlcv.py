from typing import Optional
from sqlalchemy.sql import func
from trader.connections.database import DBSession
from trader.data.base import CURRENCY_TYPE_STANDARD_CURRENCY, SOURCE_COIN_MARKET_CAP, TIMEFRAME_ONE_DAY
from trader.data.currency_ohlcv import update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap
from trader.models.cryptocurrency import Cryptocurrency
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVGroup, CurrencyOHLCVPull
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.tasks import app
from trader.utilities.functions import (
    datetime_to_ms_timestamp,
    fetch_base_data_id,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_DELTA_FUNCTION,
)
from trader.utilities.functions.cryptocurrency_exchange import (
    fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges,
)


@app.task
def update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task(
    base_currency_id: int, from_inclusive_ms_timestamp: int, to_exclusive_ms_timestamp: Optional[int] = None
) -> None:
    with DBSession() as session:
        base_currency = session.query(Cryptocurrency).get(base_currency_id)
    from_inclusive = ms_timestamp_to_datetime(from_inclusive_ms_timestamp)
    to_exclusive = ms_timestamp_to_datetime(to_exclusive_ms_timestamp) if to_exclusive_ms_timestamp else None
    new_records_inserted = update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(
        base_currency, from_inclusive, to_exclusive=to_exclusive
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
        coin_market_cap_id = fetch_base_data_id(SOURCE_COIN_MARKET_CAP)
        standard_currency_id = fetch_base_data_id(CURRENCY_TYPE_STANDARD_CURRENCY)
        one_day_id = fetch_base_data_id(TIMEFRAME_ONE_DAY)
        us_dollar = session.query(Currency).filter_by(symbol="USD", currency_type_id=standard_currency_id).one()
        for base_currency_id in base_currency_ids:
            base_currency = session.query(Currency).get(base_currency_id)
            if base_currency:
                cryptocurrency = base_currency.cryptocurrency
                if cryptocurrency:
                    last_date = (
                        session.query(func.max(CurrencyOHLCV.date_open))
                        .select_from(CurrencyOHLCV)
                        .join(CurrencyOHLCVPull)
                        .join(CurrencyOHLCVGroup)
                        .filter(
                            CurrencyOHLCVGroup.source_id == coin_market_cap_id,
                            CurrencyOHLCVGroup.base_currency_id == base_currency.id,
                            CurrencyOHLCVGroup.quote_currency_id == us_dollar.id,
                            CurrencyOHLCVGroup.timeframe_id == one_day_id,
                        )
                        .one_or_none()
                    )
                    if last_date:
                        target_date = last_date[0] + TIMEFRAME_UNIT_TO_DELTA_FUNCTION["d"](1)
                    else:
                        target_date = cryptocurrency.source_date_added
                    update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap_task.delay(
                        cryptocurrency.id, datetime_to_ms_timestamp(target_date)
                    )
