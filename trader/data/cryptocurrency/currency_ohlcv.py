from datetime import date, datetime
from typing import Dict, List, Optional, Union
from ccxt.base.exchange import Exchange
from trader.persistence.models import Currency, Timeframe
from trader.utilities.functions import (
    clean_range_cap,
    datetime_to_ms_timestamp,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION,
)
from trader.utilities.logging import logger


def retrieve_ohlcv_from_exchange_using_ccxt(
    exchange: Exchange,
    base_currency: Currency,
    quote_currency: Currency,
    timeframe: Timeframe,
    from_inclusive: Union[date, datetime],
    to_exclusive: Optional[Union[date, datetime]] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Union[datetime, float]]]:
    amount, unit = int(timeframe.base_label[:-1]), timeframe.base_label[-1:]
    from_inclusive = clean_range_cap(from_inclusive, unit)
    to_exclusive = (
        clean_range_cap(min(to_exclusive, datetime.utcnow()), unit)
        if to_exclusive
        else clean_range_cap(datetime.utcnow(), unit)
    )
    if not from_inclusive < to_exclusive:
        raise ValueError("From argument must be less than the to argument")
    symbol = f"{base_currency.symbol}/{quote_currency.symbol}"
    end = datetime_to_ms_timestamp(to_exclusive)
    output: List[Dict[str, Union[datetime, float]]] = []
    since = datetime_to_ms_timestamp(from_inclusive)
    while since < end:
        logger.debug(
            "Fetching records from exchange %s since %s",
            exchange.id,
            ms_timestamp_to_datetime(since).strftime("%Y-%m-%d %H:%M:%S"),
        )
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if len(data) == 0:
            since = datetime_to_ms_timestamp(
                max(
                    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION[unit](since, amount),
                    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION["d"](since, 1),
                )
            )
        else:
            logger.debug("Retrieved %i records", len(data))
            for record in data:
                if record[0] >= end:
                    break
                output.append(
                    {
                        "time": ms_timestamp_to_datetime(record[0]),
                        "open": record[1],
                        "high": record[2],
                        "low": record[3],
                        "close": record[4],
                        "volume": record[5],
                    }
                )
            else:
                since = datetime_to_ms_timestamp(
                    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION[unit](ms_timestamp_to_datetime(data[-1][0]), amount)
                )
                continue
            break
    return output
