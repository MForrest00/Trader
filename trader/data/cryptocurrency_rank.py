from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
from sqlalchemy.orm import Session
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, CRYPTOCURRENCY, UNKNOWN_CURRENCY
from trader.models.cryptocurrency import Cryptocurrency, CryptocurrencyPlatform
from trader.models.currency import Currency, CurrencyXCurrencyTag, CurrencyTag
from trader.models.cryptocurrency_rank import CryptocurrencyRank, CryptocurrencyRankSnapshot
from trader.utilities.constants import CRYPTOCURRENCY_RANK_LIMIT
from trader.utilities.functions import fetch_base_data_id, iso_time_string_to_datetime


@dataclass
class CryptocurrencyPlatformRecord:
    name: str
    symbol: str
    source_entity_id: int
    source_slug: str


@dataclass
class CryptocurrencyRankRecord:
    rank: int
    currency_name: str
    currency_symbol: str
    currency_max_supply: Optional[float]
    currency_source_entity_id: int
    currency_source_slug: str
    currency_source_date_added: datetime
    currency_source_date_last_updated: datetime
    currency_tags: List[str]
    cryptocurrency_platform: Optional[CryptocurrencyPlatformRecord]
    usd_market_cap: float
    usd_price: float
    usd_volume_24h: float
    circulating_supply: float
    total_supply: float


def insert_cryptocurrency_ranks(
    session: Session,
    source_id: int,
    cryptocurrency_rank_snapshot_id: int,
    data: List[CryptocurrencyRankRecord],
) -> None:
    cryptocurrency_id = fetch_base_data_id(CRYPTOCURRENCY)
    unknown_currency_id = fetch_base_data_id(UNKNOWN_CURRENCY)
    cryptocurrency_platforms_lookup: Dict[Tuple[str, str], CryptocurrencyPlatform] = {}
    currency_tags_lookup: Dict[str, CurrencyTag] = {}
    for record in data:
        if record.cryptocurrency_platform:
            if (
                record.cryptocurrency_platform.name,
                record.cryptocurrency_platform.symbol,
            ) not in cryptocurrency_platforms_lookup:
                cryptocurrency_platform = (
                    session.query(CryptocurrencyPlatform)
                    .filter_by(name=record.cryptocurrency_platform.name, symbol=record.cryptocurrency_platform.symbol)
                    .one_or_none()
                )
                if not cryptocurrency_platform:
                    cryptocurrency_platform = CryptocurrencyPlatform(
                        source_id=source_id,
                        name=record.cryptocurrency_platform.name,
                        symbol=record.cryptocurrency_platform.symbol,
                        source_entity_id=record.cryptocurrency_platform.source_entity_id,
                        source_slug=record.cryptocurrency_platform.source_slug,
                    )
                    session.add(cryptocurrency_platform)
                    session.flush()
                cryptocurrency_platforms_lookup[
                    (record.cryptocurrency_platform.name, record.cryptocurrency_platform.symbol)
                ] = cryptocurrency_platform
            else:
                cryptocurrency_platform = cryptocurrency_platforms_lookup[
                    (record.cryptocurrency_platform.name, record.cryptocurrency_platform.symbol)
                ]
            cryptocurrency_platform_id = cryptocurrency_platform.id
        else:
            cryptocurrency_platform_id = None
        currency = (
            session.query(Currency)
            .filter(
                Currency.symbol == record.currency_symbol,
                Currency.currency_type_id.in_([cryptocurrency_id, unknown_currency_id]),
            )
            .one_or_none()
        )
        if not currency:
            currency = Currency(
                source_id=source_id,
                name=record.currency_name,
                symbol=record.currency_symbol,
                currency_type_id=cryptocurrency_id,
            )
            session.add(currency)
            session.flush()
        elif currency.currency_type_id == unknown_currency_id:
            currency.source_id = source_id
            currency.name = record.currency_name
            currency.currency_type_id = cryptocurrency_id
        cryptocurrency = currency.cryptocurrency
        if not cryptocurrency:
            cryptocurrency = Cryptocurrency(
                currency_id=currency.id,
                max_supply=record.currency_max_supply,
                source_entity_id=record.currency_source_entity_id,
                source_slug=record.currency_source_slug,
                source_date_added=record.currency_source_date_added,
                source_date_last_updated=record.currency_source_date_last_updated,
                cryptocurrency_platform_id=cryptocurrency_platform_id,
            )
            session.add(cryptocurrency)
            session.flush()
        elif cryptocurrency.source_date_last_updated < record.currency_source_date_last_updated:
            cryptocurrency.max_supply = record.currency_max_supply
            cryptocurrency.source_entity_id = record.currency_source_entity_id
            cryptocurrency.source_slug = record.currency_source_slug
            cryptocurrency.source_date_added = record.currency_source_date_added
            cryptocurrency.source_date_last_updated = record.currency_source_date_last_updated
            cryptocurrency.cryptocurrency_platform_id = cryptocurrency_platform_id
            for item in currency.currency_tags:
                if item.currency_tag.tag not in record.currency_tags:
                    item.is_active = False
        for tag in record.currency_tags:
            if tag not in currency_tags_lookup:
                currency_tag = session.query(CurrencyTag).filter_by(tag=tag).one_or_none()
                if not currency_tag:
                    currency_tag = CurrencyTag(source_id=source_id, tag=tag)
                    session.add(currency_tag)
                    session.flush()
                currency_tags_lookup[tag] = currency_tag
            else:
                currency_tag = currency_tags_lookup[tag]
            currency_currency_tag = (
                session.query(CurrencyXCurrencyTag)
                .filter_by(currency_id=currency.id, currency_tag_id=currency_tag.id)
                .one_or_none()
            )
            if not currency_currency_tag:
                currency_currency_tag = CurrencyXCurrencyTag(
                    source_id=source_id,
                    currency_id=currency.id,
                    currency_tag_id=currency_tag.id,
                )
                session.add(currency_currency_tag)
            elif not currency_currency_tag.is_active:
                currency_currency_tag.is_active = True
        cryptocurrency_rank = CryptocurrencyRank(
            cryptocurrency_rank_snapshot_id=cryptocurrency_rank_snapshot_id,
            cryptocurrency_id=cryptocurrency.id,
            rank=record.rank,
            usd_market_cap=record.usd_market_cap,
            usd_price=record.usd_price,
            usd_volume_24h=record.usd_volume_24h,
            circulating_supply=record.circulating_supply,
            total_supply=record.total_supply,
        )
        session.add(cryptocurrency_rank)
    session.commit()


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
                if snapshot_date.date() != datetime.now(timezone.utc).date():
                    output.append(snapshot_date)
    return output


def retrieve_historical_cryptocurrency_ranks_from_coin_market_cap(
    snapshot_date: datetime, limit: int
) -> List[CryptocurrencyRankRecord]:
    query_string = urlencode(
        {
            "start": 1,
            "limit": limit,
            "date": snapshot_date.strftime("%Y-%m-%d"),
            "convert": "USD,USD",
        }
    )
    response = requests.get(f"https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/historical?{query_string}")
    data = response.json()
    output: List[CryptocurrencyRankRecord] = []
    for currency in data["data"]:
        if currency["platform"]:
            cryptocurrency_platform = CryptocurrencyPlatformRecord(
                name=currency["platform"]["name"],
                symbol=currency["platform"]["symbol"],
                source_entity_id=currency["platform"]["id"],
                source_slug=currency["platform"]["slug"],
            )
        else:
            cryptocurrency_platform = None
        output.append(
            CryptocurrencyRankRecord(
                rank=currency["cmc_rank"],
                currency_name=currency["name"],
                currency_symbol=currency["symbol"],
                currency_max_supply=currency["max_supply"] if currency["max_supply"] is not None else None,
                currency_source_entity_id=currency["id"],
                currency_source_slug=currency["slug"],
                currency_source_date_added=iso_time_string_to_datetime(currency["date_added"]),
                currency_source_date_last_updated=iso_time_string_to_datetime(currency["last_updated"]),
                currency_tags=[t.lower() for t in currency["tags"]],
                cryptocurrency_platform=cryptocurrency_platform,
                usd_market_cap=currency["quote"]["USD"]["market_cap"]
                if currency["quote"]["USD"]["market_cap"] is not None
                else None,
                usd_price=currency["quote"]["USD"]["price"],
                usd_volume_24h=currency["quote"]["USD"]["volume_24h"],
                circulating_supply=currency["circulating_supply"]
                if currency["circulating_supply"] is not None
                else None,
                total_supply=currency["total_supply"] if currency["total_supply"] is not None else None,
            )
        )
    return output


def retrieve_current_cryptocurrency_ranks_from_coin_market_cap(limit: int) -> List[CryptocurrencyRankRecord]:
    query_string = urlencode(
        {
            "start": 1,
            "limit": limit,
            "sortBy": "market_cap",
            "sortType": "desc",
            "convert": "USD",
            "cryptoType": "all",
            "tagType": "all",
            "audited": "false",
        }
    )
    response = requests.get(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?{query_string}")
    data = response.json()
    output: List[CryptocurrencyRankRecord] = []
    for currency in data["data"]["cryptoCurrencyList"]:
        if "platform" in currency and currency["platform"]:
            cryptocurrency_platform = CryptocurrencyPlatformRecord(
                name=currency["platform"]["name"],
                symbol=currency["platform"]["symbol"],
                source_entity_id=currency["platform"]["id"],
                source_slug=currency["platform"]["slug"],
            )
        else:
            cryptocurrency_platform = None
        output.append(
            CryptocurrencyRankRecord(
                rank=currency["cmcRank"],
                currency_name=currency["name"],
                currency_symbol=currency["symbol"],
                currency_max_supply=currency.get("maxSupply"),
                currency_source_entity_id=currency["id"],
                currency_source_slug=currency["slug"],
                currency_source_date_added=iso_time_string_to_datetime(currency["dateAdded"]),
                currency_source_date_last_updated=iso_time_string_to_datetime(currency["lastUpdated"]),
                currency_tags=[t.lower() for t in currency["tags"]],
                cryptocurrency_platform=cryptocurrency_platform,
                usd_market_cap=currency["quotes"][0]["marketCap"],
                usd_price=currency["quotes"][0]["price"],
                usd_volume_24h=currency["quotes"][0]["volume24h"],
                circulating_supply=currency["circulatingSupply"],
                total_supply=currency["totalSupply"],
            )
        )
    return output


def update_historical_cryptocurrency_ranks_from_coin_market_cap(limit: int = CRYPTOCURRENCY_RANK_LIMIT) -> None:
    coin_market_cap_id = fetch_base_data_id(COIN_MARKET_CAP)
    historical_snapshots = retrieve_historical_snapshot_list_from_coin_market_cap()
    with DBSession() as session:
        for historical_snapshot in historical_snapshots:
            cryptocurrency_rank_snapshot = (
                session.query(CryptocurrencyRankSnapshot)
                .filter_by(source_id=coin_market_cap_id, snapshot_date=historical_snapshot, is_historical=True)
                .first()
            )
            if not cryptocurrency_rank_snapshot:
                data = retrieve_historical_cryptocurrency_ranks_from_coin_market_cap(historical_snapshot, limit)
                cryptocurrency_rank_snapshot = CryptocurrencyRankSnapshot(
                    source_id=coin_market_cap_id,
                    snapshot_date=historical_snapshot,
                    is_historical=True,
                )
                session.add(cryptocurrency_rank_snapshot)
                session.flush()
                insert_cryptocurrency_ranks(session, coin_market_cap_id, cryptocurrency_rank_snapshot.id, data)


def update_current_cryptocurrency_ranks_from_coin_market_cap(limit: int = CRYPTOCURRENCY_RANK_LIMIT) -> None:
    coin_market_cap_id = fetch_base_data_id(COIN_MARKET_CAP)
    data = retrieve_current_cryptocurrency_ranks_from_coin_market_cap(limit)
    with DBSession() as session:
        cryptocurrency_rank_snapshot = CryptocurrencyRankSnapshot(
            source_id=coin_market_cap_id,
            snapshot_date=datetime.now(timezone.utc),
            is_historical=False,
        )
        session.add(cryptocurrency_rank_snapshot)
        session.flush()
        insert_cryptocurrency_ranks(session, coin_market_cap_id, cryptocurrency_rank_snapshot.id, data)
