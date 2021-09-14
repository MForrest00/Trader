from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode
from ccxt.base.exchange import Exchange
import requests
from trader.connections.database import DBSession
from trader.data.base import CURRENCY_TYPE_STANDARD_CURRENCY, SOURCE_COIN_MARKET_CAP, TIMEFRAME_ONE_DAY
from trader.models.cryptocurrency import Cryptocurrency
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVGroup, CurrencyOHLCVPull
from trader.models.timeframe import Timeframe
from trader.utilities.functions import (
    clean_range_cap,
    datetime_to_ms_timestamp,
    fetch_base_data_id,
    iso_time_string_to_datetime,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_DELTA_FUNCTION,
)


def retrieve_cryptocurrency_ohlcv_from_exchange_using_ccxt(
    exchange: Exchange,
    base_currency: Cryptocurrency,
    quote_currency: Currency,
    timeframe: Timeframe,
    from_inclusive: datetime,
    to_exclusive: Optional[datetime] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Union[datetime, float]]]:
    from_inclusive = clean_range_cap(from_inclusive, timeframe.unit)
    to_exclusive = (
        clean_range_cap(min(to_exclusive, datetime.now(timezone.utc)), timeframe.unit)
        if to_exclusive
        else clean_range_cap(datetime.now(timezone.utc), timeframe.unit)
    )
    if not from_inclusive < to_exclusive:
        raise ValueError("From argument must be less than the to argument")
    symbol = f"{base_currency.currency.symbol}/{quote_currency.symbol}"
    end = datetime_to_ms_timestamp(to_exclusive)
    output: List[Dict[str, Union[datetime, float]]] = []
    since = datetime_to_ms_timestamp(from_inclusive)
    while since < end:
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=limit)
        if len(data) == 0:
            since = datetime_to_ms_timestamp(
                max(
                    since + TIMEFRAME_UNIT_TO_DELTA_FUNCTION[timeframe.unit](timeframe.amount),
                    since + TIMEFRAME_UNIT_TO_DELTA_FUNCTION["d"](1),
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
                    ms_timestamp_to_datetime(data[-1][0])
                    + TIMEFRAME_UNIT_TO_DELTA_FUNCTION[timeframe.unit](timeframe.amount)
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
) -> int:
    coin_market_cap_id = fetch_base_data_id(SOURCE_COIN_MARKET_CAP)
    standard_currency_id = fetch_base_data_id(CURRENCY_TYPE_STANDARD_CURRENCY)
    one_day_id = fetch_base_data_id(TIMEFRAME_ONE_DAY)
    data = retrieve_cryptocurrency_daily_usd_ohlcv_from_coin_market_cap(base_currency, from_inclusive, to_exclusive)
    with DBSession() as session:
        us_dollar = session.query(Currency).filter_by(symbol="USD", currency_type_id=standard_currency_id).one()
        currency_ohlcv_group = (
            session.query(CurrencyOHLCVGroup)
            .filter_by(
                source_id=coin_market_cap_id,
                base_currency_id=base_currency.currency.id,
                quote_currency_id=us_dollar.id,
                timeframe_id=one_day_id,
            )
            .one_or_none()
        )
        if not currency_ohlcv_group:
            currency_ohlcv_group = CurrencyOHLCVGroup(
                source_id=coin_market_cap_id,
                base_currency_id=base_currency.currency.id,
                quote_currency_id=us_dollar.id,
                timeframe_id=one_day_id,
            )
            session.add(currency_ohlcv_group)
            session.flush()
        currency_ohlcv_pull = CurrencyOHLCVPull(
            currency_ohlcv_group_id=currency_ohlcv_group.id,
            from_inclusive=from_inclusive,
            to_exclusive=to_exclusive,
        )
        session.add(currency_ohlcv_pull)
        session.flush()
        new_records_inserted = 0
        if data:
            existing_records = (
                session.query(CurrencyOHLCV)
                .join(CurrencyOHLCVPull)
                .join(CurrencyOHLCVGroup)
                .filter(
                    CurrencyOHLCVGroup.source_id == coin_market_cap_id,
                    CurrencyOHLCVGroup.base_currency_id == base_currency.currency.id,
                    CurrencyOHLCVGroup.quote_currency_id == us_dollar.id,
                    CurrencyOHLCVGroup.timeframe_id == one_day_id,
                    CurrencyOHLCV.date_open >= data[0]["date_open"],
                    CurrencyOHLCV.date_open <= data[-1]["date_open"],
                )
                .all()
            )
            existing_date_opens = set(r.date_open for r in existing_records)
            for record in data:
                if record["date_open"] not in existing_date_opens:
                    currency_ohlcv = CurrencyOHLCV(currency_ohlcv_pull_id=currency_ohlcv_pull.id, **record)
                    session.add(currency_ohlcv)
                    new_records_inserted += 1
        session.commit()
    return new_records_inserted
