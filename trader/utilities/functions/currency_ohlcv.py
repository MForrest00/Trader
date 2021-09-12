from datetime import datetime
from typing import Optional
import pandas as pd
from trader.connections.database import DBSession
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVGroup, CurrencyOHLCVPull
from trader.models.source import Source
from trader.models.timeframe import Timeframe


def fetch_currency_ohlcv_as_dataframe(
    source: Source,
    base_currency: Currency,
    quote_currency: Currency,
    timeframe: Timeframe,
    from_inclusive: Optional[datetime] = None,
    to_exclusive: Optional[datetime] = None,
) -> pd.DataFrame:
    with DBSession() as session:
        records_query = (
            session.query(CurrencyOHLCV)
            .join(CurrencyOHLCVPull)
            .join(CurrencyOHLCVGroup)
            .filter(
                CurrencyOHLCVGroup.source_id == source.id,
                CurrencyOHLCVGroup.base_currency_id == base_currency.id,
                CurrencyOHLCVGroup.quote_currency_id == quote_currency.id,
                CurrencyOHLCVGroup.timeframe_id == timeframe.id,
            )
            .order_by(CurrencyOHLCV.date_open.asc())
        )
        if from_inclusive:
            records_query.filter(CurrencyOHLCV.date_open >= from_inclusive)
        if to_exclusive:
            records_query.filter(CurrencyOHLCV.date_open < to_exclusive)
        records = records_query.all()
    return pd.DataFrame(
        (
            {"id": r.id, "open": r.open, "high": r.high, "low": r.low, "close": r.close, "volume": r.volume}
            for r in records
        ),
        index=(r.date_open for r in records),
    )
