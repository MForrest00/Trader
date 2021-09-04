from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode
from ccxt.base.exchange import Exchange
import requests
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, ONE_DAY, STANDARD_CURRENCY
from trader.models.cryptocurrency import Cryptocurrency
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVPull
from trader.models.timeframe import Timeframe
from trader.utilities.functions import (
    clean_range_cap,
    datetime_to_ms_timestamp,
    fetch_base_data_id,
    iso_time_string_to_datetime,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION,
)


def retrieve_cryptocurrency_ohlcv_from_exchange_using_ccxt(
    exchange: Exchange,
    base_cryptocurrency: Cryptocurrency,
    quote_currency: Currency,
    timeframe: Timeframe,
    from_inclusive: datetime,
    to_exclusive: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Union[datetime, float]]]:
    amount, unit = int(timeframe.base_label[:-1]), timeframe.base_label[-1:]
    from_inclusive = clean_range_cap(from_inclusive, unit)
    to_exclusive = (
        clean_range_cap(min(to_exclusive, datetime.now(timezone.utc)), unit)
        if to_exclusive
        else clean_range_cap(datetime.now(timezone.utc), unit)
    )
    if not from_inclusive < to_exclusive:
        raise ValueError("From argument must be less than the to argument")
    symbol = f"{base_cryptocurrency.currency.symbol}/{quote_currency.symbol}"
    end = datetime_to_ms_timestamp(to_exclusive)
    output: List[Dict[str, Union[datetime, float]]] = []
    since = datetime_to_ms_timestamp(from_inclusive)
    while since < end:
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if len(data) == 0:
            since = datetime_to_ms_timestamp(
                max(
                    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION[unit](since, amount),
                    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION["d"](since, 1),
                )
            )
        else:
            for record in data:
                if record[0] >= end:
                    break
                output.append(
                    {
                        "date_open": ms_timestamp_to_datetime(record[0]),
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


def retrieve_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(
    base_currency: Cryptocurrency,
    from_inclusive: datetime,
    to_exclusive: Optional[datetime] = None,
) -> List[Dict[str, Union[datetime, float]]]:
    if base_currency.source_entity_id is None:
        raise ValueError("Unable to pull data for currency {base_currency.currency.name}")
    from_timestamp = int(clean_range_cap(from_inclusive, "d").timestamp())
    to_exclusive = min(to_exclusive, datetime.now(timezone.utc)) if to_exclusive else datetime.now(timezone.utc)
    to_timestamp = int((clean_range_cap(to_exclusive, "d") - timedelta(days=1)).timestamp())
    query_string = urlencode(
        {
            "id": base_currency.source_entity_id,
            "convertId": 2781,
            "timeStart": from_timestamp,
            "timeEnd": to_timestamp,
        }
    )
    response = requests.get(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?{query_string}")
    data = response.json()
    output: List[Dict[str, Union[datetime, float]]] = []
    for record in data["data"]["quotes"]:
        try:
            date_high = iso_time_string_to_datetime(record["timeHigh"]) if "timeHigh" in record else None
        except ValueError:
            date_high = None
        try:
            date_low = iso_time_string_to_datetime(record["timeLow"]) if "timeLow" in record else None
        except ValueError:
            date_low = None
        output.append(
            {
                "date_open": iso_time_string_to_datetime(record["timeOpen"]),
                "open": record["quote"]["open"],
                "high": record["quote"]["high"],
                "low": record["quote"]["low"],
                "close": record["quote"]["close"],
                "volume": record["quote"]["volume"],
                "date_high": date_high,
                "date_low": date_low,
            }
        )
    return output


def update_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(
    base_currency: Cryptocurrency, from_inclusive: datetime, to_exclusive: Optional[datetime] = None
) -> None:
    coin_market_cap_id = fetch_base_data_id(COIN_MARKET_CAP)
    standard_currency_id = fetch_base_data_id(STANDARD_CURRENCY)
    one_day_id = fetch_base_data_id(ONE_DAY)
    data = retrieve_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(base_currency, from_inclusive, to_exclusive)
    with DBSession() as session:
        us_dollar = session.query(Currency).filter_by(symbol="USD", currency_type_id=standard_currency_id).one()
        currency_ohlcv_pull = CurrencyOHLCVPull(
            source_id=coin_market_cap_id,
            base_currency_id=base_currency.currency.id,
            quote_currency_id=us_dollar.id,
            timeframe_id=one_day_id,
            from_inclusive=from_inclusive,
            to_exclusive=to_exclusive,
        )
        session.add(currency_ohlcv_pull)
        session.flush()
        for record in data:
            currency_ohlcv = CurrencyOHLCV(currency_ohlcv_pull_id=currency_ohlcv_pull.id, **record)
            session.add(currency_ohlcv)
        session.commit()
