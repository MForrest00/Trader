from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.models.currency import CurrencyType
from trader.models.data_feed import DataFeed
from trader.models.google_trends import GoogleTrendsGeo, GoogleTrendsGprop
from trader.models.source import Source, SourceType
from trader.models.timeframe import Timeframe
from trader.models.user import User


@dataclass
class CurrencyTypeData:
    cache_key: str
    description: str


CURRENCY_TYPE_UNKNOWN_CURRENCY = CurrencyTypeData("currency_type_unknown_currency_id", "Unknown currency")
CURRENCY_TYPE_STANDARD_CURRENCY = CurrencyTypeData("currency_type_standard_currency_id", "Standard currency")
CURRENCY_TYPE_CRYPTOCURRENCY = CurrencyTypeData("currency_type_cryptocurrency_id", "Cryptocurrency")
CURRENCY_TYPES = (CURRENCY_TYPE_UNKNOWN_CURRENCY, CURRENCY_TYPE_STANDARD_CURRENCY, CURRENCY_TYPE_CRYPTOCURRENCY)


def initialize_currency_types(session: Session) -> None:
    for currency_type in CURRENCY_TYPES:
        instance = session.query(CurrencyType).filter_by(description=currency_type.description).one_or_none()
        if not instance:
            instance = CurrencyType(description=currency_type.description)
            session.add(instance)
            session.flush()
        cache.set(currency_type.cache_key, instance.id)


@dataclass
class GoogleTrendsGeoData:
    cache_key: str
    code: str
    name: str


GOOGLE_TRENDS_GEO_WORLDWIDE = GoogleTrendsGeoData("google_trends_geo_worldwide_id", "", "Worldwide")
GOOGLE_TRENDS_GEO_UNITED_STATES = GoogleTrendsGeoData("google_trends_geo_united_states_id", "US", "United States")
GOOGLE_TRENDS_GEOS = (GOOGLE_TRENDS_GEO_WORLDWIDE, GOOGLE_TRENDS_GEO_UNITED_STATES)


def initialize_google_trends_geos(session: Session) -> None:
    for google_trends_geo in GOOGLE_TRENDS_GEOS:
        instance = session.query(GoogleTrendsGeo).filter_by(code=google_trends_geo.code).one_or_none()
        if not instance:
            instance = GoogleTrendsGeo(code=google_trends_geo.code, name=google_trends_geo.name)
            session.add(instance)
            session.flush()
        cache.set(google_trends_geo.cache_key, instance.id)


@dataclass
class GoogleTrendsGpropData:
    cache_key: str
    code: str
    name: str


GOOGLE_TRENDS_GPROP_WEB_SEARCH = GoogleTrendsGpropData("google_trends_gprop_web_search_id", "", "Web search")
GOOGLE_TRENDS_GPROP_IMAGE_SEARCH = GoogleTrendsGpropData("google_trends_gprop_image_search_id", "image", "Image search")
GOOGLE_TRENDS_GPROP_NEWS_SEARCH = GoogleTrendsGpropData("google_trends_gprop_news_search_id", "news", "News search")
GOOGLE_TRENDS_GPROP_GOOGLE_SHOPPING = GoogleTrendsGpropData(
    "google_trends_gprop_google_shopping_id", "froogle", "Google shopping"
)
GOOGLE_TRENDS_GPROP_YOUTUBE_SEARCH = GoogleTrendsGpropData(
    "google_trends_gprop_youtube_search_id", "youtube", "YouTube search"
)
GOOGLE_TRENDS_GPROPS = (
    GOOGLE_TRENDS_GPROP_WEB_SEARCH,
    GOOGLE_TRENDS_GPROP_IMAGE_SEARCH,
    GOOGLE_TRENDS_GPROP_NEWS_SEARCH,
    GOOGLE_TRENDS_GPROP_GOOGLE_SHOPPING,
    GOOGLE_TRENDS_GPROP_YOUTUBE_SEARCH,
)


def initialize_google_trends_gprops(session: Session) -> None:
    for google_trends_gprop in GOOGLE_TRENDS_GPROPS:
        instance = session.query(GoogleTrendsGprop).filter_by(code=google_trends_gprop.code).one_or_none()
        if not instance:
            instance = GoogleTrendsGprop(code=google_trends_gprop.code, name=google_trends_gprop.name)
            session.add(instance)
            session.flush()
        cache.set(google_trends_gprop.cache_key, instance.id)


@dataclass
class SourceTypeData:
    cache_key: str
    description: str


SOURCE_TYPE_MISCELLANEOUS_DATA = SourceTypeData("source_type_miscellaneous_data_id", "Miscellaneous data")
SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA = SourceTypeData(
    "source_type_cryptocurrency_market_data_id", "Cryptocurrency market data"
)
SOURCE_TYPE_CRYPTOCURRENCY_EXCHANGE = SourceTypeData(
    "source_type_cryptocurrency_exchange_id", "Cryptocurrency exchange"
)
SOURCE_TYPE_SEARCH_DATA = SourceTypeData("source_type_search_data_id", "Search data")
SOURCE_TYPES = (
    SOURCE_TYPE_MISCELLANEOUS_DATA,
    SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA,
    SOURCE_TYPE_CRYPTOCURRENCY_EXCHANGE,
    SOURCE_TYPE_SEARCH_DATA,
)


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


SOURCE_ISO = SourceData("source_iso_id", None, "ISO", SOURCE_TYPE_MISCELLANEOUS_DATA, url="https://www.iso.org/")
SOURCE_COIN_MARKET_CAP = SourceData(
    "source_coin_market_cap_id",
    None,
    "CoinMarketCap",
    SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA,
    url="https://coinmarketcap.com/",
)
SOURCE_COIN_GECKO = SourceData(
    "source_coin_gecko_id", None, "CoinGecko", SOURCE_TYPE_CRYPTOCURRENCY_MARKET_DATA, url="https://www.coingecko.com/"
)
SOURCE_GOOGLE_TRENDS = SourceData(
    "source_google_trends_id", None, "Google Trends", SOURCE_TYPE_SEARCH_DATA, url="https://trends.google.com/"
)
SOURCES = (SOURCE_ISO, SOURCE_COIN_MARKET_CAP, SOURCE_COIN_GECKO, SOURCE_GOOGLE_TRENDS)


def initialize_sources(session: Session) -> None:
    for source in SOURCES:
        source_type_id = int(cache.get(source.source_type.cache_key).decode())
        instance = session.query(Source).filter_by(source_type_id=source_type_id, name=source.name).one_or_none()
        if not instance:
            instance = Source(source_type_id=source_type_id, name=source.name, url=source.url)
            session.add(instance)
            session.flush()
        cache.set(source.cache_key, instance.id)


@dataclass
class TimeframeData:
    cache_key: str
    base_label: str
    seconds_length: Optional[int]
    unit: str
    amount: int
    ccxt_label: str


TIMEFRAME_ONE_MINUTE = TimeframeData("timeframe_one_minute_id", "1m", 60, "m", 1, "1m")
TIMEFRAME_FIVE_MINUTE = TimeframeData("timeframe_five_minute_id", "5m", 60 * 5, "m", 5, "5m")
TIMEFRAME_EIGHT_MINUTE = TimeframeData("timeframe_eight_minute_id", "8m", 60 * 8, "m", 8, "8m")
TIMEFRAME_FIFTEEN_MINUTE = TimeframeData("timeframe_fifteen_minute_id", "15m", 60 * 15, "m", 15, "15m")
TIMEFRAME_THIRTY_MINUTE = TimeframeData("timeframe_thirty_minute_id", "30m", 60 * 30, "m", 30, "30m")
TIMEFRAME_ONE_HOUR = TimeframeData("timeframe_one_hour_id", "1h", 60 * 60, "h", 1, "1h")
TIMEFRAME_ONE_DAY = TimeframeData("timeframe_one_day_id", "1d", 60 * 60 * 24, "d", 1, "1d")
TIMEFRAME_ONE_MONTH = TimeframeData("timeframe_one_month_id", "1M", None, "M", 1, "1M")
TIMEFRAMES = (
    TIMEFRAME_ONE_MINUTE,
    TIMEFRAME_FIVE_MINUTE,
    TIMEFRAME_EIGHT_MINUTE,
    TIMEFRAME_FIFTEEN_MINUTE,
    TIMEFRAME_THIRTY_MINUTE,
    TIMEFRAME_ONE_HOUR,
    TIMEFRAME_ONE_DAY,
    TIMEFRAME_ONE_MONTH,
)


def initialize_timeframes(session: Session) -> None:
    for timeframe in TIMEFRAMES:
        instance = session.query(Timeframe).filter_by(base_label=timeframe.base_label).one_or_none()
        if not instance:
            instance = Timeframe(
                base_label=timeframe.base_label,
                seconds_length=timeframe.seconds_length,
                unit=timeframe.unit,
                amount=timeframe.amount,
                ccxt_label=timeframe.ccxt_label,
            )
            session.add(instance)
            session.flush()
        cache.set(timeframe.cache_key, instance.id)


@dataclass
class DataFeedData:
    cache_key: str
    name: str


DATA_FEED_CURRENCY_OHLCV = DataFeedData("data_feed_currency_ohlcv_id", "Currency OHLCV")
DATA_FEED_GOOGLE_TRENDS = DataFeedData("data_feed_google_trends_id", "Google Trends")
DATA_FEEDS = (DATA_FEED_CURRENCY_OHLCV, DATA_FEED_GOOGLE_TRENDS)


def initialize_data_feeds(session: Session) -> None:
    for data_feed in DATA_FEEDS:
        instance = session.query(DataFeed).filter_by(name=data_feed.name).one_or_none()
        if not instance:
            instance = DataFeed(name=data_feed.name)
            session.add(instance)
            session.flush()
        cache.set(data_feed.cache_key, instance.id)


@dataclass
class UserData:
    cache_key: str
    first_name: str
    last_name: str
    email: str


USER_ADMIN = UserData("user_admin_id", "admin", "user", "admin@email.com")
USERS = (USER_ADMIN,)


def initialize_users(session: Session) -> None:
    for user in USERS:
        instance = session.query(User).filter_by(email=user.email).one_or_none()
        if not instance:
            instance = User(first_name=user.first_name, last_name=user.last_name, email=user.email)
            session.add(instance)
            session.flush()
        cache.set(user.cache_key, instance.id)


def initialize_base_data() -> None:
    with DBSession() as session:
        initialize_currency_types(session)
        initialize_google_trends_geos(session)
        initialize_google_trends_gprops(session)
        initialize_source_types(session)
        initialize_sources(session)
        initialize_timeframes(session)
        initialize_data_feeds(session)
        initialize_users(session)
        session.commit()
