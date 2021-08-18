from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import sessionmaker
from trader.connections.cache import cache
from trader.connections.database import database
from trader.persistence.models.google_trends import GoogleTrendsPullGeo
from trader.persistence.models.source import Source, SourceType
from trader.persistence.models.timeframe import Timeframe


@dataclass
class SourceTypeData:
    cache_key: str
    description: str


BASE_DATA_TYPE = SourceTypeData("source_type_base_data_type_id", "Base data type")
CRYPTOCURRENCY_MARKET_DATA = SourceTypeData("source_type_cryptocurrency_market_data_id", "Cryptocurrency market data")
CRYPTOCURRENCY_EXCHANGE = SourceTypeData("source_type_cryptocurrency_exchange_id", "Cryptocurrency exchange")
WEB_SEARCH_DATA = SourceTypeData("source_type_web_search_data_id", "Web search data")
SOURCE_TYPES = (BASE_DATA_TYPE, CRYPTOCURRENCY_MARKET_DATA, CRYPTOCURRENCY_EXCHANGE, WEB_SEARCH_DATA)


@dataclass
class SourceData:
    cache_key: str
    name: str
    source_type: SourceTypeData
    url: Optional[str] = None


BASE_DATA = SourceData("source_base_data_id", "Base Data", BASE_DATA_TYPE)
COIN_MARKET_CAP = SourceData(
    "source_coin_market_cap_id", "CoinMarketCap", CRYPTOCURRENCY_MARKET_DATA, url="https://coinmarketcap.com/"
)
GOOGLE_TRENDS = SourceData(
    "source_google_trends_id", "Google Trends", WEB_SEARCH_DATA, url="https://trends.google.com/"
)
SOURCES = (BASE_DATA, COIN_MARKET_CAP, GOOGLE_TRENDS)


@dataclass
class TimeframeData:
    cache_key: str
    base_label: str
    seconds_length: Optional[int]
    ccxt_label: str


ONE_MINUTE = TimeframeData("timeframe_1m", "1m", 60, "1m")
FIVE_MINUTE = TimeframeData("timeframe_5m", "5m", 60 * 5, "5m")
EIGHT_MINUTE = TimeframeData("timeframe_8m", "8m", 60 * 8, "8m")
FIFTEEN_MINUTE = TimeframeData("timeframe_15m", "15m", 60 * 15, "15m")
THIRTY_MINUTE = TimeframeData("timeframe_30m", "30m", 60 * 30, "30m")
ONE_HOUR = TimeframeData("timeframe_1h", "1h", 60 * 60, "1h")
ONE_DAY = TimeframeData("timeframe_1d", "1d", 60 * 60 * 24, "1d")
ONE_MONTH = TimeframeData("timeframe_1M", "1M", None, "1M")
TIMEFRAMES = (ONE_MINUTE, FIVE_MINUTE, EIGHT_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE, ONE_HOUR, ONE_DAY, ONE_MONTH)


@dataclass
class GoogleTrendsPullGeoData:
    cache_key: str
    code: str
    name: str


WORLDWIDE = GoogleTrendsPullGeoData("google_trends_pull_geo_worldwide", "", "Worldwide")
UNITED_STATES = GoogleTrendsPullGeoData("google_trends_pull_geo_worldwide", "US", "United States")
GOOGLE_TRENDS_PULL_GEOS = (WORLDWIDE, UNITED_STATES)


def initialize_base_data() -> None:
    Session = sessionmaker(database)
    with Session() as session:
        for source_type in SOURCE_TYPES:
            instance = session.query(SourceType).filter(SourceType.description == source_type.description).first()
            if not instance:
                instance = SourceType(description=source_type.description)
                session.add(instance)
                session.commit()
            cache.set(source_type.cache_key, instance.id)
        for source in SOURCES:
            source_type_id = int(cache.get(source.source_type.cache_key).decode())
            instance = (
                session.query(Source)
                .filter(Source.name == source.name, Source.source_type_id == source_type_id, Source.url == source.url)
                .first()
            )
            if not instance:
                instance = Source(
                    name=source.name,
                    source_type_id=source_type_id,
                    url=source.url,
                )
                session.add(instance)
                session.commit()
            cache.set(source.cache_key, instance.id)
        for timeframe in TIMEFRAMES:
            instance = (
                session.query(Timeframe)
                .filter(
                    Timeframe.base_label == timeframe.base_label,
                    Timeframe.seconds_length == timeframe.seconds_length,
                    Timeframe.ccxt_label == timeframe.ccxt_label,
                )
                .first()
            )
            if not instance:
                instance = Timeframe(
                    base_label=timeframe.base_label,
                    seconds_length=timeframe.seconds_length,
                    ccxt_label=timeframe.ccxt_label,
                )
                session.add(instance)
                session.commit()
            cache.set(timeframe.cache_key, instance.id)
        for google_trends_pull_geo in GOOGLE_TRENDS_PULL_GEOS:
            instance = (
                session.query(GoogleTrendsPullGeo)
                .filter(
                    GoogleTrendsPullGeo.code == google_trends_pull_geo.code,
                    GoogleTrendsPullGeo.name == google_trends_pull_geo.name,
                )
                .first()
            )
            if not instance:
                instance = GoogleTrendsPullGeo(code=google_trends_pull_geo.code, name=google_trends_pull_geo.name)
                session.add(instance)
                session.commit()
            cache.set(google_trends_pull_geo.cache_key, instance.id)
