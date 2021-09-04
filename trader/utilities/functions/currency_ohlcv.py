import pandas as pd
from trader.connections.database import DBSession
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVPull
from trader.models.source import Source
from trader.models.timeframe import Timeframe


def fetch_currency_ohlcv_as_dataframe(
    source: Source, base_currency: Currency, quote_currency: Currency, timeframe: Timeframe
) -> pd.DataFrame:
    with DBSession() as session:
        records = (
            session.query(CurrencyOHLCV)
            .join(CurrencyOHLCVPull)
            .filter(
                CurrencyOHLCVPull.source_id == source.id,
                CurrencyOHLCVPull.base_currency_id == base_currency.id,
                CurrencyOHLCVPull.quote_currency_id == quote_currency.id,
                CurrencyOHLCVPull.timeframe_id == timeframe.id,
            )
            .order_by(CurrencyOHLCV.date_open.asc())
            .all()
        )
    return pd.DataFrame(
        ({"open": r.open, "high": r.high, "low": r.low, "close": r.close, "volume": r.volume} for r in records),
        index=(r.date_open for r in records),
    )
