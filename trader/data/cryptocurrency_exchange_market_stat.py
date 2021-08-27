from urllib.parse import urlencode
from typing import Dict
import requests
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, UNKNOWN_CURRENCY
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import (
    CryptocurrencyExchangeMarket,
    CryptocurrencyExchangeMarketCategory,
    CryptocurrencyExchangeMarketFeeType,
)
from trader.models.cryptocurrency_exchange_market_stat import (
    CryptocurrencyExchangeMarketStat,
    CryptocurrencyExchangeMarketStatPull,
)
from trader.utilities.functions import iso_time_string_to_datetime


def update_cryptocurrency_exchange_ranks_from_coin_market_cap(cryptocurrency_exchange: CryptocurrencyExchange) -> None:
    if cryptocurrency_exchange.source_slug is None:
        raise ValueError("Unable to pull data for cryptocurrency exchange {cryptocurrency_exchange.source.name}")
    coin_market_cap_id = int(cache.get(COIN_MARKET_CAP.cache_key).decode())
    unknown_currency_id = int(cache.get(UNKNOWN_CURRENCY.cache_key).decode())
    start = 1
    limit = 100
    with DBSession() as session:
        cryptocurrency_exchange_rank_pull = CryptocurrencyExchangeMarketStatPull(
            source_id=coin_market_cap_id, cryptocurrency_exchange_id=cryptocurrency_exchange.id
        )
        session.add(cryptocurrency_exchange_rank_pull)
        session.flush()
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
            cryptocurrency_exchange_market_fee_types: Dict[str, CryptocurrencyExchangeMarketFeeType] = {}
            cryptocurrency_exchange_market_categories: Dict[str, CryptocurrencyExchangeMarketCategory] = {}
            for market_pair in market_pairs:
                cryptocurrency_exchange_market_fee_type_description = market_pair["feeType"].lower()
                cryptocurrency_exchange_market_category_description = market_pair["category"].lower()
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
            start += limit
        session.commit()
