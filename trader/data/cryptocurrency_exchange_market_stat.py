from urllib.parse import urlencode
from typing import Dict, Tuple
import requests
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, CRYPTOCURRENCY, STANDARD_CURRENCY, UNKNOWN_CURRENCY
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import (
    CryptocurrencyExchangeMarket,
    CryptocurrencyExchangeMarketCategory,
    CryptocurrencyExchangeMarketFeeType,
)
from trader.models.currency import Currency
from trader.models.cryptocurrency_exchange_market_stat import (
    CryptocurrencyExchangeMarketStat,
    CryptocurrencyExchangeMarketStatPull,
)
from trader.utilities.functions import iso_time_string_to_datetime


def update_cryptocurrency_exchange_ranks_from_coin_market_cap(cryptocurrency_exchange: CryptocurrencyExchange) -> None:
    if cryptocurrency_exchange.source_slug is None:
        raise ValueError("Unable to pull data for cryptocurrency exchange {cryptocurrency_exchange.source.name}")
    coin_market_cap_id = int(cache.get(COIN_MARKET_CAP.cache_key).decode())
    cryptocurrency_id = int(cache.get(CRYPTOCURRENCY.cache_key).decode())
    standard_currency_id = int(cache.get(STANDARD_CURRENCY.cache_key).decode())
    unknown_currency_id = int(cache.get(UNKNOWN_CURRENCY.cache_key).decode())
    currency_type_ids = (cryptocurrency_id, standard_currency_id, unknown_currency_id)
    start = 1
    limit = 100
    with DBSession() as session:
        cryptocurrency_exchange_market_stat_pull = CryptocurrencyExchangeMarketStatPull(
            source_id=coin_market_cap_id, cryptocurrency_exchange_id=cryptocurrency_exchange.id
        )
        session.add(cryptocurrency_exchange_market_stat_pull)
        session.flush()
        cryptocurrency_exchange_market_fee_types: Dict[str, CryptocurrencyExchangeMarketFeeType] = {}
        cryptocurrency_exchange_market_categories: Dict[str, CryptocurrencyExchangeMarketCategory] = {}
        currencies: Dict[Tuple[str, int], Currency] = {}
        while True:
            query_string = urlencode(
                {
                    "start": start,
                    "limit": limit,
                    "slug": cryptocurrency_exchange.source_slug,
                    "category": "all",
                }
            )
            response = requests.get(
                f"https://api.coinmarketcap.com/data-api/v3/exchange/market-pairs/latest?{query_string}"
            )
            data = response.json()
            market_pairs = data["data"]["marketPairs"]
            if len(market_pairs) == 0:
                break
            for market_pair in market_pairs:
                cryptocurrency_exchange_market_fee_type_description = market_pair["feeType"].lower()
                if cryptocurrency_exchange_market_fee_type_description not in cryptocurrency_exchange_market_fee_types:
                    cryptocurrency_exchange_market_fee_type = (
                        session.query(CryptocurrencyExchangeMarketFeeType)
                        .filter_by(description=cryptocurrency_exchange_market_fee_type_description)
                        .one_or_none()
                    )
                    if not cryptocurrency_exchange_market_fee_type:
                        cryptocurrency_exchange_market_fee_type = CryptocurrencyExchangeMarketFeeType(
                            source_id=coin_market_cap_id,
                            description=cryptocurrency_exchange_market_fee_type_description,
                        )
                        session.add(cryptocurrency_exchange_market_fee_type)
                        session.flush()
                    cryptocurrency_exchange_market_fee_types[
                        cryptocurrency_exchange_market_fee_type_description
                    ] = cryptocurrency_exchange_market_fee_type
                else:
                    cryptocurrency_exchange_market_fee_type = cryptocurrency_exchange_market_fee_types[
                        cryptocurrency_exchange_market_fee_type_description
                    ]
                cryptocurrency_exchange_market_category_description = market_pair["category"].lower()
                if cryptocurrency_exchange_market_category_description not in cryptocurrency_exchange_market_categories:
                    cryptocurrency_exchange_market_category = (
                        session.query(CryptocurrencyExchangeMarketCategory)
                        .filter_by(description=cryptocurrency_exchange_market_category_description)
                        .one_or_none()
                    )
                    if not cryptocurrency_exchange_market_category:
                        cryptocurrency_exchange_market_category = CryptocurrencyExchangeMarketCategory(
                            source_id=coin_market_cap_id,
                            description=cryptocurrency_exchange_market_category_description,
                        )
                        session.add(cryptocurrency_exchange_market_category)
                        session.flush()
                    cryptocurrency_exchange_market_categories[
                        cryptocurrency_exchange_market_category_description
                    ] = cryptocurrency_exchange_market_category
                else:
                    cryptocurrency_exchange_market_category = cryptocurrency_exchange_market_categories[
                        cryptocurrency_exchange_market_category_description
                    ]
                base_currency_symbol = market_pair["baseSymbol"]
                for currency_type_id in currency_type_ids:
                    if (base_currency_symbol, currency_type_id) not in currencies:
                        base_currency = (
                            session.query(Currency)
                            .filter_by(symbol=base_currency_symbol, currency_type_id=currency_type_id)
                            .one_or_none()
                        )
                        currencies[(base_currency_symbol, currency_type_id)] = base_currency
                    else:
                        base_currency = currencies[(base_currency_symbol, currency_type_id)]
                    if base_currency:
                        break
                else:
                    base_currency = Currency(
                        source_id=coin_market_cap_id,
                        name=market_pair["baseCurrencyName"],
                        symbol=base_currency_symbol,
                        currency_type_id=unknown_currency_id,
                    )
                    session.add(base_currency)
                    session.flush()
                    currencies[(base_currency_symbol, unknown_currency_id)] = base_currency
                quote_currency_symbol = market_pair["quoteSymbol"]
                for currency_type_id in currency_type_ids:
                    if (quote_currency_symbol, currency_type_id) not in currencies:
                        quote_currency = (
                            session.query(Currency)
                            .filter_by(symbol=quote_currency_symbol, currency_type_id=currency_type_id)
                            .one_or_none()
                        )
                        currencies[(quote_currency_symbol, currency_type_id)] = quote_currency
                    else:
                        quote_currency = currencies[(quote_currency_symbol, currency_type_id)]
                    if quote_currency:
                        break
                else:
                    quote_currency = Currency(
                        source_id=coin_market_cap_id,
                        symbol=quote_currency_symbol,
                        currency_type_id=unknown_currency_id,
                    )
                    session.add(quote_currency)
                    session.flush()
                    currencies[(quote_currency_symbol, unknown_currency_id)] = quote_currency
                cryptocurrency_exchange_market = (
                    session.query(CryptocurrencyExchangeMarket)
                    .filter_by(
                        cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                        cryptocurrency_exchange_market_category_id=cryptocurrency_exchange_market_category.id,
                        base_currency_id=base_currency.id,
                        quote_currency_id=quote_currency.id,
                    )
                    .one_or_none()
                )
                cryptocurrency_exchange_market_url = market_pair["marketUrl"]
                cryptocurrency_exchange_market_source_entity_id = market_pair["marketId"]
                cryptocurrency_exchange_source_date_last_updated = iso_time_string_to_datetime(
                    market_pair["lastUpdated"]
                )
                if not cryptocurrency_exchange_market:
                    cryptocurrency_exchange_market = CryptocurrencyExchangeMarket(
                        source_id=coin_market_cap_id,
                        cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                        cryptocurrency_exchange_market_category_id=cryptocurrency_exchange_market_category.id,
                        base_currency_id=base_currency.id,
                        quote_currency_id=quote_currency.id,
                        cryptocurrency_exchange_market_fee_type_id=cryptocurrency_exchange_market_fee_type.id,
                        market_url=cryptocurrency_exchange_market_url,
                        source_entity_id=cryptocurrency_exchange_market_source_entity_id,
                        source_date_last_updated=cryptocurrency_exchange_source_date_last_updated,
                    )
                    session.add(cryptocurrency_exchange_market)
                    session.flush()
                elif (
                    cryptocurrency_exchange_market.source_date_last_updated
                    < cryptocurrency_exchange_source_date_last_updated
                ):
                    cryptocurrency_exchange_market.update(
                        {
                            "source_id": coin_market_cap_id,
                            "cryptocurrency_exchange_market_fee_type_id": cryptocurrency_exchange_market_fee_type.id,
                            "market_url": cryptocurrency_exchange_market_url,
                            "source_entity_id": cryptocurrency_exchange_market_source_entity_id,
                            "source_date_last_updated": cryptocurrency_exchange_source_date_last_updated,
                        }
                    )
                cryptocurrency_exchange_market_stat = CryptocurrencyExchangeMarketStat(
                    cryptocurrency_exchange_market_stat_pull_id=cryptocurrency_exchange_market_stat_pull.id,
                    cryptocurrency_exchange_market_id=cryptocurrency_exchange_market.id,
                    price=market_pair["price"],
                    usd_volume_24h=market_pair["volumeUsd"],
                    base_currency_volume_24h=market_pair["volumeBase"],
                    quote_currency_volume_24h=market_pair["volumeQuote"],
                    usd_depth_negative_two=market_pair["depthUsdNegativeTwo"],
                    usd_depth_positive_two=market_pair["depthUsdPositiveTwo"],
                    source_score=market_pair["marketScore"],
                    source_liquidity_score=market_pair["effectiveLiquidity"],
                    source_reputation=market_pair["marketReputation"],
                    source_outlier_detected=market_pair["outlierDetected"],
                    source_price_excluded=market_pair["priceExcluded"],
                    source_volume_excluded=market_pair["volumeExcluded"],
                )
                session.add(cryptocurrency_exchange_market_stat)
            start += limit
        session.commit()
