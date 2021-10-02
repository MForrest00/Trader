from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
from trader.connections.database import session
from trader.data.initial.asset_type import ASSET_TYPE_CRYPTOCURRENCY, ASSET_TYPE_UNKNOWN_CURRENCY
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.models.asset import AssetTag, AssetXAssetTag, Asset
from trader.models.cryptocurrency import Cryptocurrency, CryptocurrencyPlatform
from trader.models.cryptocurrency_rank import CryptocurrencyRank, CryptocurrencyRankSnapshot
from trader.utilities.functions import iso_time_string_to_datetime


CRYPTOCURRENCY_RANK_LIMIT = 500


@dataclass
class CryptocurrencyPlatformRecord:
    name: str
    symbol: str
    coin_market_cap_id: int
    coin_market_cap_slug: str


@dataclass
class CryptocurrencyRankRecord:
    rank: int
    asset_name: str
    asset_symbol: str
    asset_tags: List[str]
    cryptocurrency_max_supply: Optional[float]
    cryptocurrency_coin_market_cap_id: int
    cryptocurrency_coin_market_cap_slug: str
    cryptocurrency_coin_market_cap_date_added: datetime
    cryptocurrency_coin_market_cap_date_last_updated: datetime
    cryptocurrency_platform: Optional[CryptocurrencyPlatformRecord]
    usd_market_cap: float
    usd_price: float
    usd_volume_24h: float
    circulating_supply: float
    total_supply: float


def insert_cryptocurrency_ranks(
    source_id: int, cryptocurrency_rank_snapshot_id: int, data: List[CryptocurrencyRankRecord]
) -> None:
    cryptocurrency_id = ASSET_TYPE_CRYPTOCURRENCY.fetch_id()
    unknown_currency_id = ASSET_TYPE_UNKNOWN_CURRENCY.fetch_id()
    cryptocurrency_platforms_lookup: Dict[Tuple[str, str], CryptocurrencyPlatform] = {}
    asset_tags_lookup: Dict[str, AssetTag] = {}
    for record in data:
        if record.cryptocurrency_platform:
            cryptocurrency_platform_key = (record.cryptocurrency_platform.name, record.cryptocurrency_platform.symbol)
            if cryptocurrency_platform_key not in cryptocurrency_platforms_lookup:
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
                        coin_market_cap_id=record.cryptocurrency_platform.coin_market_cap_id,
                        coin_market_cap_slug=record.cryptocurrency_platform.coin_market_cap_slug,
                    )
                    session.add(cryptocurrency_platform)
                    session.flush()
                cryptocurrency_platforms_lookup[cryptocurrency_platform_key] = cryptocurrency_platform
            else:
                cryptocurrency_platform = cryptocurrency_platforms_lookup[cryptocurrency_platform_key]
            cryptocurrency_platform_id = cryptocurrency_platform.id
        else:
            cryptocurrency_platform_id = None
        asset = (
            session.query(Asset)
            .filter(
                Asset.asset_type_id.in_([cryptocurrency_id, unknown_currency_id]),
                Asset.symbol == record.asset_symbol,
            )
            .one_or_none()
        )
        if not asset:
            asset = Asset(
                source_id=source_id,
                asset_type_id=cryptocurrency_id,
                name=record.asset_name,
                symbol=record.asset_symbol,
            )
            session.add(asset)
            session.flush()
        elif asset.asset_type_id == unknown_currency_id:
            asset.source_id = source_id
            asset.asset_type_id = cryptocurrency_id
            asset.name = record.asset_name
        cryptocurrency = asset.cryptocurrency
        if not cryptocurrency:
            cryptocurrency = Cryptocurrency(
                asset_id=asset.id,
                max_supply=record.cryptocurrency_max_supply,
                coin_market_cap_id=record.cryptocurrency_coin_market_cap_id,
                coin_market_cap_slug=record.cryptocurrency_coin_market_cap_slug,
                coin_market_cap_date_added=record.cryptocurrency_coin_market_cap_date_added,
                coin_market_cap_date_last_updated=record.cryptocurrency_coin_market_cap_date_last_updated,
                cryptocurrency_platform_id=cryptocurrency_platform_id,
            )
            session.add(cryptocurrency)
            session.flush()
        elif cryptocurrency.coin_market_cap_date_last_updated < record.cryptocurrency_coin_market_cap_date_last_updated:
            cryptocurrency.max_supply = record.cryptocurrency_max_supply
            cryptocurrency.coin_market_cap_id = record.cryptocurrency_coin_market_cap_id
            cryptocurrency.coin_market_cap_slug = record.cryptocurrency_coin_market_cap_slug
            cryptocurrency.coin_market_cap_date_added = record.cryptocurrency_coin_market_cap_date_added
            cryptocurrency.coin_market_cap_date_last_updated = record.cryptocurrency_coin_market_cap_date_last_updated
            cryptocurrency.cryptocurrency_platform_id = cryptocurrency_platform_id
            for item in asset.asset_tags:
                if item.asset_tag.tag not in record.asset_tags:
                    item.is_active = False
        for tag in record.asset_tags:
            if tag not in asset_tags_lookup:
                asset_tag = session.query(AssetTag).filter_by(tag=tag).one_or_none()
                if not asset_tag:
                    asset_tag = AssetTag(source_id=source_id, tag=tag)
                    session.add(asset_tag)
                    session.flush()
                asset_tags_lookup[tag] = asset_tag
            else:
                asset_tag = asset_tags_lookup[tag]
            asset_x_asset_tag = (
                session.query(AssetXAssetTag).filter_by(asset_id=asset.id, asset_tag_id=asset_tag.id).one_or_none()
            )
            if not asset_x_asset_tag:
                asset_x_asset_tag = AssetXAssetTag(
                    source_id=source_id,
                    asset_id=asset.id,
                    asset_tag_id=asset_tag.id,
                )
                session.add(asset_x_asset_tag)
            elif not asset_x_asset_tag.is_active:
                asset_x_asset_tag.is_active = True
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
                coin_market_cap_id=currency["platform"]["id"],
                coin_market_cap_slug=currency["platform"]["slug"],
            )
        else:
            cryptocurrency_platform = None
        output.append(
            CryptocurrencyRankRecord(
                rank=currency["cmc_rank"],
                asset_name=currency["name"],
                asset_symbol=currency["symbol"],
                asset_tags=[t.lower() for t in currency["tags"]],
                cryptocurrency_max_supply=currency["max_supply"] if currency["max_supply"] is not None else None,
                cryptocurrency_coin_market_cap_id=currency["id"],
                cryptocurrency_coin_market_cap_slug=currency["slug"],
                cryptocurrency_coin_market_cap_date_added=iso_time_string_to_datetime(currency["date_added"]),
                cryptocurrency_coin_market_cap_date_last_updated=iso_time_string_to_datetime(currency["last_updated"]),
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
                coin_market_cap_id=currency["platform"]["id"],
                coin_market_cap_slug=currency["platform"]["slug"],
            )
        else:
            cryptocurrency_platform = None
        output.append(
            CryptocurrencyRankRecord(
                rank=currency["cmcRank"],
                asset_name=currency["name"],
                asset_symbol=currency["symbol"],
                asset_tags=[t.lower() for t in currency["tags"]],
                cryptocurrency_max_supply=currency.get("maxSupply"),
                cryptocurrency_coin_market_cap_id=currency["id"],
                cryptocurrency_coin_market_cap_slug=currency["slug"],
                cryptocurrency_coin_market_cap_date_added=iso_time_string_to_datetime(currency["dateAdded"]),
                cryptocurrency_coin_market_cap_date_last_updated=iso_time_string_to_datetime(currency["lastUpdated"]),
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
    coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
    historical_snapshots = retrieve_historical_snapshot_list_from_coin_market_cap()
    for historical_snapshot in historical_snapshots:
        cryptocurrency_rank_snapshot = (
            session.query(CryptocurrencyRankSnapshot)
            .filter_by(source_id=coin_market_cap_id, snapshot_date=historical_snapshot, is_historical=True)
            .one_or_none()
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
            insert_cryptocurrency_ranks(coin_market_cap_id, cryptocurrency_rank_snapshot.id, data)
            session.commit()


def update_current_cryptocurrency_ranks_from_coin_market_cap(limit: int = CRYPTOCURRENCY_RANK_LIMIT) -> None:
    coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
    data = retrieve_current_cryptocurrency_ranks_from_coin_market_cap(limit)
    cryptocurrency_rank_snapshot = CryptocurrencyRankSnapshot(
        source_id=coin_market_cap_id,
        snapshot_date=datetime.now(timezone.utc),
        is_historical=False,
    )
    session.add(cryptocurrency_rank_snapshot)
    session.flush()
    insert_cryptocurrency_ranks(coin_market_cap_id, cryptocurrency_rank_snapshot.id, data)
    session.commit()
