from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Union
from bs4 import BeautifulSoup
from ccxt.base.exchange import Exchange
import requests
from sqlalchemy.orm import Session, sessionmaker
from trader.connections.cache import cache
from trader.connections.database import database
from trader.persistence.base_data import COIN_MARKET_CAP
from trader.persistence.models import (
    Currency,
    CurrencyCurrencyTag,
    CurrencyPlatform,
    CurrencyTag,
    Timeframe,
    TopCryptocurrencySnapshot,
    TopCryptocurrency,
)
from trader.utilities.constants import TOP_CRYPTOCURRENCY_LIMIT
from trader.utilities.functions import (
    clean_range_cap,
    datetime_to_ms_timestamp,
    ms_timestamp_to_datetime,
    TIMEFRAME_UNIT_TO_INCREMENT_FUNCTION,
)
from trader.utilities.logging import logger


def fetch_ohlcv_from_exchange(
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


def retrieve_historical_snapshot_list_from_coin_market_cap() -> List[datetime]:
    response = requests.get("https://coinmarketcap.com/historical/")
    soup = BeautifulSoup(response.text, "lxml")
    table_wrapper = soup.select("div.cmc-bottom-margin-2x")[0]
    year_rows = table_wrapper.find_all("div", recursive=False)[:-1]
    month_name_to_number = {datetime(1970, i, 1).strftime("%B"): i for i in range(1, 13)}
    output: List[datetime] = []
    for year_row in year_rows:
        header, body = year_row.find_all("div", recursive=False)
        year = int(header.text)
        month_sections = body.find_all("div", recursive=False)
        for month_section in month_sections:
            month = month_section.find("div", recursive=False).find("div", recursive=False).text
            historical_snapshots = month_section.find("div", recursive=False).find_all("a", recursive=False, href=True)
            for historical_snapshot in historical_snapshots:
                day = int(historical_snapshot.text)
                snapshot_date = datetime(year, month_name_to_number[month], day, tzinfo=timezone.utc)
                if snapshot_date.date() != datetime.utcnow().date():
                    output.append()
    return output


@dataclass
class CryptocurrencyPlatformRecord:
    name: str
    symbol: str


@dataclass
class TopCryptocurrencyRecord:
    rank: int
    currency_name: str
    currency_symbol: str
    currency_max_supply: Optional[Decimal]
    currency_source_date_added: datetime
    currency_tags: List[str]
    currency_platform: Optional[CryptocurrencyPlatformRecord]
    usd_market_cap: Decimal
    usd_price: Decimal
    circulating_supply: Decimal
    total_supply: Decimal


def insert_top_cryptocurrencies(
    session: Session,
    source_id: int,
    snapshot_date: datetime,
    is_historical: bool,
    data: List[TopCryptocurrencyRecord],
) -> None:
    top_cryptocurrency_snapshot = TopCryptocurrencySnapshot(
        source_id=source_id,
        snapshot_date=snapshot_date,
        is_historical=is_historical,
    )
    session.add(top_cryptocurrency_snapshot)
    session.flush()
    for record in data:
        if record.currency_platform:
            currency_platform = (
                session.query(CurrencyPlatform)
                .filter(
                    CurrencyPlatform.name == record.currency_platform.name,
                    CurrencyPlatform.symbol == record.currency_platform.symbol,
                )
                .first()
            )
            if not currency_platform:
                currency_platform = CurrencyPlatform(
                    source_id=source_id,
                    name=record.currency_platform.name,
                    symbol=record.currency_platform.symbol,
                )
                session.add(currency_platform)
                session.flush()
            currency_platform_id = currency_platform.id
        else:
            currency_platform_id = None
        currency = (
            session.query(Currency)
            .filter(
                Currency.name == record.currency_name,
                Currency.symbol == record.currency_symbol,
                Currency.is_cryptocurrency.is_(True),
            )
            .first()
        )
        if not currency:
            currency = Currency(
                source_id=source_id,
                name=record.currency_name,
                symbol=record.currency_symbol,
                is_cryptocurrency=True,
                max_supply=record.currency_max_supply,
                source_date_added=record.currency_source_date_added,
                currency_platform_id=currency_platform_id,
            )
            session.add(currency)
            session.flush()
        for tag in record.currency_tags:
            currency_tag = session.query(CurrencyTag).filter(CurrencyTag.tag == tag).first()
            if not currency_tag:
                currency_tag = CurrencyTag(source_id=source_id, tag=tag)
                session.add(currency_tag)
                session.flush()
            currency_currency_tag = (
                session.query(CurrencyCurrencyTag)
                .filter(
                    CurrencyCurrencyTag.currency_id == currency.id,
                    CurrencyCurrencyTag.currency_tag_id == currency_tag.id,
                )
                .first()
            )
            if not currency_currency_tag:
                currency_currency_tag = CurrencyCurrencyTag(
                    source_id=source_id,
                    currency_id=currency.id,
                    currency_tag_id=currency_tag.id,
                )
                session.add(currency_currency_tag)
                session.flush()
        top_cryptocurrency = TopCryptocurrency(
            top_cryptocurrency_snapshot_id=top_cryptocurrency_snapshot.id,
            rank=record.rank,
            currency_id=currency.id,
            usd_market_cap=record.usd_market_cap,
            usd_price=record.usd_price,
            circulating_supply=record.circulating_supply,
            total_supply=record.total_supply,
        )
        session.add(top_cryptocurrency)
    session.commit()


def capture_historical_top_cryptocurrencies_from_coin_market_cap(
    snapshot_date: datetime,
) -> List[TopCryptocurrencyRecord]:
    url = (
        "https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/historical?convert=USD,USD&date="
        + f"{snapshot_date.strftime('%Y-%m-%d')}&limit={TOP_CRYPTOCURRENCY_LIMIT}&start=1"
    )
    response = requests.get(url)
    data = response.json()
    output: List[TopCryptocurrencyRecord] = []
    for currency in data["data"]:
        if currency["platform"]:
            currency_platform = CryptocurrencyPlatformRecord(
                name=currency["platform"]["name"],
                symbol=currency["platform"]["symbol"],
            )
        else:
            currency_platform = None
        output.append(
            TopCryptocurrencyRecord(
                rank=currency["cmc_rank"],
                currency_name=currency["name"],
                currency_symbol=currency["symbol"],
                currency_max_supply=Decimal(currency["max_supply"]) if currency["max_supply"] else None,
                currency_source_date_added=datetime.strptime(currency["date_added"], "%Y-%m-%dT%H:%M:%S.%f%z"),
                currency_tags=currency["tags"],
                currency_platform=currency_platform,
                usd_market_cap=Decimal(currency["quote"]["USD"]["market_cap"]),
                usd_price=Decimal(currency["quote"]["USD"]["price"]),
                circulating_supply=Decimal(currency["circulating_supply"]),
                total_supply=Decimal(currency["total_supply"]),
            )
        )
    return output


def capture_current_top_cryptocurrencies_from_coin_market_cap() -> List[TopCryptocurrencyRecord]:
    url = (
        f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit={TOP_CRYPTOCURRENCY_LIMIT}&"
        + "sortBy=market_cap&sortType=desc&convert=USD&cryptoType=all&tagType=all&audited=false"
    )
    response = requests.get(url)
    data = response.json()
    output: List[TopCryptocurrencyRecord] = []
    for currency in data["data"]["cryptoCurrencyList"]:
        if "platform" in currency and currency["platform"]:
            currency_platform = CryptocurrencyPlatformRecord(
                name=currency["platform"]["name"],
                symbol=currency["platform"]["symbol"],
            )
        else:
            currency_platform = None
        output.append(
            TopCryptocurrencyRecord(
                rank=currency["cmcRank"],
                currency_name=currency["name"],
                currency_symbol=currency["symbol"],
                currency_max_supply=Decimal(currency["maxSupply"]) if "maxSupply" in currency else None,
                currency_source_date_added=datetime.strptime(currency["dateAdded"], "%Y-%m-%dT%H:%M:%S.%f%z"),
                currency_tags=currency["tags"],
                currency_platform=currency_platform,
                usd_market_cap=Decimal(currency["quotes"][0]["marketCap"]),
                usd_price=Decimal(currency["quotes"][0]["price"]),
                circulating_supply=Decimal(currency["circulatingSupply"]),
                total_supply=Decimal(currency["totalSupply"]),
            )
        )
    return output


def update_top_cryptocurrencies_from_coin_market_cap() -> None:
    coin_market_cap_id = int(cache.get(COIN_MARKET_CAP.cache_key).decode())
    historical_snapshots = retrieve_historical_snapshot_list_from_coin_market_cap()
    Session = sessionmaker(database)
    with Session() as session:
        for historical_snapshot in historical_snapshots:
            top_cryptocurrency_snapshot = (
                session.query(TopCryptocurrencySnapshot)
                .filter(
                    TopCryptocurrencySnapshot.source_id == coin_market_cap_id,
                    TopCryptocurrencySnapshot.snapshot_date == historical_snapshot,
                    TopCryptocurrencySnapshot.is_historical.is_(True),
                )
                .first()
            )
            if not top_cryptocurrency_snapshot:
                logger.debug(
                    "Fetching data for historical top cryptocurrencies snapshot for date %s",
                    historical_snapshot.strftime("%Y-%m-%d"),
                )
                data = capture_historical_top_cryptocurrencies_from_coin_market_cap(historical_snapshot)
                if data:
                    insert_top_cryptocurrencies(session, coin_market_cap_id, historical_snapshot, True, data)
        logger.debug("Fetching data for current top cryptocurrencies")
        data = capture_current_top_cryptocurrencies_from_coin_market_cap()
        if data:
            insert_top_cryptocurrencies(session, coin_market_cap_id, datetime.utcnow(), False, data)
