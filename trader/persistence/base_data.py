from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import sessionmaker
from trader.connections.cache import cache
from trader.connections.database import database
from trader.persistence.models import Currency, CurrencyPlatform, Source, SourceType


@dataclass
class SourceTypeData:
    cache_key: str
    description: str


DATA_ONLY = SourceTypeData("source_type_data_only_id", "Data only")
CRYPTOCURRENCY_EXCHANGE = SourceTypeData("source_type_cryptocurrency_exchange_id", "Cryptocurrency exchange")
SOURCE_TYPES = (DATA_ONLY, CRYPTOCURRENCY_EXCHANGE)


@dataclass
class SourceData:
    cache_key: str
    name: str
    source_type: SourceTypeData
    url: Optional[str] = None


BASE_DATA = SourceData("source_base_data_id", "Base Data", DATA_ONLY)
COIN_MARKET_CAP = SourceData("source_coin_market_cap_id", "CoinMarketCap", DATA_ONLY, url="https://coinmarketcap.com/")
BINANCE = SourceData("source_binance_id", "Binance", CRYPTOCURRENCY_EXCHANGE, url="https://www.binance.com/")
SOURCES = (BASE_DATA, COIN_MARKET_CAP, BINANCE)


@dataclass
class CurrencyPlatformData:
    cache_key: str
    source: SourceData
    name: str
    symbol: str


CURRENCY_PLATFORMS = ()


@dataclass
class CurrencyData:
    cache_key: str
    source: SourceData
    name: str
    symbol: str
    is_cryptocurrency: bool = True
    max_supply: Optional[Decimal] = None
    source_date_added: Optional[datetime] = None
    currency_platform: Optional[CurrencyPlatformData] = None


UNITED_STATES_DOLLAR = CurrencyData(
    "currency_united_states_dollar_id", BASE_DATA, "United States Dollar", "USD", is_cryptocurrency=False
)
CURRENCIES = (UNITED_STATES_DOLLAR,)


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
        for currency_platform in CURRENCY_PLATFORMS:
            instance = (
                session.query(CurrencyPlatform)
                .filter(
                    CurrencyPlatform.name == currency_platform.name,
                    CurrencyPlatform.symbol == currency_platform.symbol,
                )
                .first()
            )
            if not instance:
                instance = CurrencyPlatform(
                    source_id=int(cache.get(currency_platform.source.cache_key).decode()),
                    name=currency_platform.name,
                    symbol=currency_platform.symbol,
                )
                session.add(instance)
                session.commit()
            cache.set(currency_platform.cache_key, instance.id)
        for currency in CURRENCIES:
            instance = (
                session.query(Currency)
                .filter(
                    Currency.name == currency.name,
                    Currency.symbol == currency.symbol,
                    Currency.is_cryptocurrency == currency.is_cryptocurrency,
                )
                .first()
            )
            if not instance:
                currency_platform_id = (
                    int(cache.get(currency.currency_platform.cache_key).decode())
                    if currency.currency_platform
                    else None
                )
                instance = Currency(
                    source_id=int(cache.get(currency.source.cache_key).decode()),
                    name=currency.name,
                    symbol=currency.symbol,
                    is_cryptocurrency=currency.is_cryptocurrency,
                    max_supply=currency.max_supply,
                    source_date_added=currency.source_date_added,
                    currency_platform_id=currency_platform_id,
                )
                session.add(instance)
                session.commit()
            cache.set(currency.cache_key, instance.id)
