from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.models.currency import CurrencyType
from trader.models.currency_strategy import CurrencyStrategyType
from trader.models.google_trends import GoogleTrendsPullGeo, GoogleTrendsPullGprop
from trader.models.source import Source, SourceType
from trader.models.timeframe import Timeframe


@dataclass
class CurrencyTypeData:
    cache_key: str
    description: str


UNKNOWN_CURRENCY = CurrencyTypeData("currency_type_unknown_currency_id", "Unknown currency")
STANDARD_CURRENCY = CurrencyTypeData("currency_type_standard_currency_id", "Standard currency")
CRYPTOCURRENCY = CurrencyTypeData("currency_type_cryptocurrency_id", "Cryptocurrency")
CURRENCY_TYPES = (UNKNOWN_CURRENCY, STANDARD_CURRENCY, CRYPTOCURRENCY)


def initialize_currency_types(session: Session) -> None:
    for currency_type in CURRENCY_TYPES:
        instance = session.query(CurrencyType).filter_by(description=currency_type.description).one_or_none()
        if not instance:
            instance = CurrencyType(description=currency_type.description)
            session.add(instance)
            session.flush()
        cache.set(currency_type.cache_key, instance.id)


@dataclass
class GoogleTrendsPullGeoData:
    cache_key: str
    code: str
    name: str


WORLDWIDE = GoogleTrendsPullGeoData("google_trends_pull_geo_worldwide_id", "", "Worldwide")
UNITED_STATES = GoogleTrendsPullGeoData("google_trends_pull_geo_united_states_id", "US", "United States")
GOOGLE_TRENDS_PULL_GEOS = (WORLDWIDE, UNITED_STATES)


def initialize_google_trends_pull_geos(session: Session) -> None:
    for google_trends_pull_geo in GOOGLE_TRENDS_PULL_GEOS:
        instance = session.query(GoogleTrendsPullGeo).filter_by(code=google_trends_pull_geo.code).one_or_none()
        if not instance:
            instance = GoogleTrendsPullGeo(code=google_trends_pull_geo.code, name=google_trends_pull_geo.name)
            session.add(instance)
            session.flush()
        cache.set(google_trends_pull_geo.cache_key, instance.id)


@dataclass
class GoogleTrendsPullGpropData:
    cache_key: str
    code: str
    name: str


WEB_SEARCH = GoogleTrendsPullGpropData("google_trends_pull_gprop_web_search_id", "", "Web search")
IMAGE_SEARCH = GoogleTrendsPullGpropData("google_trends_pull_gprop_image_search_id", "image", "Image search")
NEWS_SEARCH = GoogleTrendsPullGpropData("google_trends_pull_gprop_news_search_id", "news", "News search")
GOOGLE_SHOPPING = GoogleTrendsPullGpropData("google_trends_pull_gprop_google_shopping_id", "froogle", "Google shopping")
YOUTUBE_SEARCH = GoogleTrendsPullGpropData("google_trends_pull_gprop_youtube_search_id", "youtube", "YouTube search")
GOOGLE_TRENDS_PULL_GPROPS = (WEB_SEARCH, IMAGE_SEARCH, NEWS_SEARCH, GOOGLE_SHOPPING, YOUTUBE_SEARCH)


def initialize_google_trends_pull_gprops(session: Session) -> None:
    for google_trends_pull_gprop in GOOGLE_TRENDS_PULL_GPROPS:
        instance = session.query(GoogleTrendsPullGprop).filter_by(code=google_trends_pull_gprop.code).one_or_none()
        if not instance:
            instance = GoogleTrendsPullGprop(code=google_trends_pull_gprop.code, name=google_trends_pull_gprop.name)
            session.add(instance)
            session.flush()
        cache.set(google_trends_pull_gprop.cache_key, instance.id)


@dataclass
class SourceTypeData:
    cache_key: str
    description: str


MISCELLANEOUS_DATA = SourceTypeData("source_type_miscellaneous_data_id", "Miscellaneous data")
CRYPTOCURRENCY_MARKET_DATA = SourceTypeData("source_type_cryptocurrency_market_data_id", "Cryptocurrency market data")
CRYPTOCURRENCY_EXCHANGE = SourceTypeData("source_type_cryptocurrency_exchange_id", "Cryptocurrency exchange")
SEARCH_DATA = SourceTypeData("source_type_search_data_id", "Search data")
SOURCE_TYPES = (MISCELLANEOUS_DATA, CRYPTOCURRENCY_MARKET_DATA, CRYPTOCURRENCY_EXCHANGE, SEARCH_DATA)


def initialize_source_types(session: Session) -> None:
    for source_type in SOURCE_TYPES:
        instance = session.query(SourceType).filter_by(description=source_type.description).one_or_none()
        if not instance:
            instance = SourceType(description=source_type.description)
            session.add(instance)
            session.flush()
        cache.set(source_type.cache_key, instance.id)


@dataclass
class SourceData:
    cache_key: str
    source_id: Optional[int]
    name: str
    source_type: SourceTypeData
    url: Optional[str] = None


ISO = SourceData("source_iso_id", None, "ISO", MISCELLANEOUS_DATA, url="https://www.iso.org/")
COIN_MARKET_CAP = SourceData(
    "source_coin_market_cap_id", None, "CoinMarketCap", CRYPTOCURRENCY_MARKET_DATA, url="https://coinmarketcap.com/"
)
COIN_GECKO = SourceData(
    "source_coin_gecko_id", None, "CoinGecko", CRYPTOCURRENCY_MARKET_DATA, url="https://www.coingecko.com/"
)
GOOGLE_TRENDS = SourceData(
    "source_google_trends_id", None, "Google Trends", SEARCH_DATA, url="https://trends.google.com/"
)
SOURCES = (ISO, COIN_MARKET_CAP, COIN_GECKO, GOOGLE_TRENDS)


def initialize_sources(session: Session) -> None:
    for source in SOURCES:
        source_type_id = int(cache.get(source.source_type.cache_key).decode())
        instance = session.query(Source).filter_by(name=source.name, source_type_id=source_type_id).one_or_none()
        if not instance:
            instance = Source(
                name=source.name,
                source_type_id=source_type_id,
                url=source.url,
            )
            session.add(instance)
            session.flush()
        cache.set(source.cache_key, instance.id)


@dataclass
class TimeframeData:
    cache_key: str
    base_label: str
    seconds_length: Optional[int]
    ccxt_label: str


ONE_MINUTE = TimeframeData("timeframe_1m_id", "1m", 60, "1m")
FIVE_MINUTE = TimeframeData("timeframe_5m_id", "5m", 60 * 5, "5m")
EIGHT_MINUTE = TimeframeData("timeframe_8m_id", "8m", 60 * 8, "8m")
FIFTEEN_MINUTE = TimeframeData("timeframe_15m_id", "15m", 60 * 15, "15m")
THIRTY_MINUTE = TimeframeData("timeframe_30m_id", "30m", 60 * 30, "30m")
ONE_HOUR = TimeframeData("timeframe_1h_id", "1h", 60 * 60, "1h")
ONE_DAY = TimeframeData("timeframe_1d_id", "1d", 60 * 60 * 24, "1d")
ONE_MONTH = TimeframeData("timeframe_1M_id", "1M", None, "1M")
TIMEFRAMES = (ONE_MINUTE, FIVE_MINUTE, EIGHT_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE, ONE_HOUR, ONE_DAY, ONE_MONTH)


def initialize_timeframes(session: Session) -> None:
    for timeframe in TIMEFRAMES:
        instance = session.query(Timeframe).filter_by(base_label=timeframe.base_label).one_or_none()
        if not instance:
            instance = Timeframe(
                base_label=timeframe.base_label,
                seconds_length=timeframe.seconds_length,
                ccxt_label=timeframe.ccxt_label,
            )
            session.add(instance)
            session.flush()
        cache.set(timeframe.cache_key, instance.id)


@dataclass
class CurrencyStrategyTypeData:
    cache_key: str
    description: str


CURRENCY_OHLCV = CurrencyStrategyTypeData("currency_strategy_type_currency_ohlcv_id", "Currency OHLCV")
CURRENCY_STRATEGY_TYPES = (CURRENCY_OHLCV,)


def initialize_currency_strategy_types(session: Session) -> None:
    for currency_strategy_type in CURRENCY_STRATEGY_TYPES:
        instance = (
            session.query(CurrencyStrategyType).filter_by(description=currency_strategy_type.description).one_or_none()
        )
        if not instance:
            instance = CurrencyStrategyType(description=currency_strategy_type.description)
            session.add(instance)
            session.flush()
        cache.set(currency_strategy_type.cache_key, instance.id)


def initialize_base_data() -> None:
    with DBSession() as session:
        initialize_currency_types(session)
        initialize_google_trends_pull_geos(session)
        initialize_google_trends_pull_gprops(session)
        initialize_source_types(session)
        initialize_sources(session)
        initialize_timeframes(session)
        initialize_currency_strategy_types(session)
        session.commit()
