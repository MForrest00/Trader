from urllib.parse import urlencode
from typing import Dict, List, Tuple, Union
import requests
from trader.connections.database import session
from trader.data.initial.asset_type import (
    ASSET_TYPE_CRYPTOCURRENCY,
    ASSET_TYPE_STANDARD_CURRENCY,
    ASSET_TYPE_UNKNOWN_CURRENCY,
)
from trader.data.initial.source import SOURCE_COIN_MARKET_CAP
from trader.models.asset import Asset
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
from trader.models.enabled_cryptocurrency_exchange import EnabledCryptocurrencyExchange
from trader.tasks import app
from trader.utilities.functions import iso_time_string_to_datetime


@app.task
def update_cryptocurrency_exchange_market_stats_from_coin_market_cap(cryptocurrency_exchange_id: int) -> None:
    cryptocurrency_exchange = session.query(CryptocurrencyExchange).get(cryptocurrency_exchange_id)
    if not cryptocurrency_exchange:
        raise ValueError("Cryptocurrency exchange does not exist with that ID")
    if cryptocurrency_exchange.coin_market_cap_slug is None:
        raise ValueError("Cryptocurrency exchange must have a coin_market_cap_slug attribute")
    coin_market_cap_id = SOURCE_COIN_MARKET_CAP.fetch_id()
    unknown_currency_id = ASSET_TYPE_UNKNOWN_CURRENCY.fetch_id()
    asset_type_ids = (
        ASSET_TYPE_CRYPTOCURRENCY.fetch_id(),
        ASSET_TYPE_STANDARD_CURRENCY.fetch_id(),
        unknown_currency_id,
    )
    market_stat_pull = CryptocurrencyExchangeMarketStatPull(
        source_id=coin_market_cap_id, cryptocurrency_exchange_id=cryptocurrency_exchange.id
    )
    session.add(market_stat_pull)
    session.flush()
    start = 1
    limit = 100
    market_pairs: List[Dict[str, Union[str, int, float]]] = []
    while True:
        query_string = urlencode(
            {
                "start": start,
                "limit": limit,
                "slug": cryptocurrency_exchange.coin_market_cap_slug,
                "category": "all",
            }
        )
        response = requests.get(
            f"https://api.coinmarketcap.com/data-api/v3/exchange/market-pairs/latest?{query_string}"
        )
        data = response.json()
        market_pairs_data = data["data"]["marketPairs"]
        if len(market_pairs_data) == 0:
            break
        market_pairs.extend(market_pairs_data)
        start += limit
    market_pair_combinations = set((r["baseSymbol"], r["quoteSymbol"], r["feeType"].lower()) for r in market_pairs)
    for market in cryptocurrency_exchange.cryptocurrency_exchange_markets:
        market_pair_combination = (
            market.base_asset.symbol,
            market.quote_asset.symbol,
            market.cryptocurrency_exchange_market_fee_type.description,
        )
        if market_pair_combination not in market_pair_combinations:
            market.is_active = False
    market_fee_types_lookup: Dict[str, CryptocurrencyExchangeMarketFeeType] = {}
    market_categories_lookup: Dict[str, CryptocurrencyExchangeMarketCategory] = {}
    asset_lookup: Dict[Tuple[int, str], Asset] = {}
    for market_pair in market_pairs:
        market_fee_type_description = market_pair["feeType"].lower()
        if market_fee_type_description not in market_fee_types_lookup:
            market_fee_type = (
                session.query(CryptocurrencyExchangeMarketFeeType)
                .filter_by(description=market_fee_type_description)
                .one_or_none()
            )
            if not market_fee_type:
                market_fee_type = CryptocurrencyExchangeMarketFeeType(
                    source_id=coin_market_cap_id, description=market_fee_type_description
                )
                session.add(market_fee_type)
                session.flush()
            market_fee_types_lookup[market_fee_type_description] = market_fee_type
        else:
            market_fee_type = market_fee_types_lookup[market_fee_type_description]
        market_category_description = market_pair["category"].lower()
        if market_category_description not in market_categories_lookup:
            market_category = (
                session.query(CryptocurrencyExchangeMarketCategory)
                .filter_by(description=market_category_description)
                .one_or_none()
            )
            if not market_category:
                market_category = CryptocurrencyExchangeMarketCategory(
                    source_id=coin_market_cap_id, description=market_category_description
                )
                session.add(market_category)
                session.flush()
            market_categories_lookup[market_category_description] = market_category
        else:
            market_category = market_categories_lookup[market_category_description]
        base_asset_symbol = market_pair["baseSymbol"]
        for asset_type_id in asset_type_ids:
            asset_key = (asset_type_id, base_asset_symbol)
            if asset_key not in asset_lookup:
                base_asset = (
                    session.query(Asset).filter_by(asset_type_id=asset_type_id, symbol=base_asset_symbol).one_or_none()
                )
                asset_lookup[asset_key] = base_asset
            else:
                base_asset = asset_lookup[asset_key]
            if base_asset:
                break
        else:
            base_asset = Asset(
                source_id=coin_market_cap_id,
                asset_type_id=unknown_currency_id,
                name=market_pair["baseCurrencyName"],
                symbol=base_asset_symbol,
            )
            session.add(base_asset)
            session.flush()
            asset_lookup[(unknown_currency_id, base_asset_symbol)] = base_asset
        quote_asset_symbol = market_pair["quoteSymbol"]
        for asset_type_id in asset_type_ids:
            asset_key = (asset_type_id, quote_asset_symbol)
            if asset_key not in asset_lookup:
                quote_asset = (
                    session.query(Asset).filter_by(asset_type_id=asset_type_id, symbol=quote_asset_symbol).one_or_none()
                )
                asset_lookup[asset_key] = quote_asset
            else:
                quote_asset = asset_lookup[asset_key]
            if quote_asset:
                break
        else:
            quote_asset = Asset(
                source_id=coin_market_cap_id,
                asset_type_id=unknown_currency_id,
                symbol=quote_asset_symbol,
            )
            session.add(quote_asset)
            session.flush()
            asset_lookup[(unknown_currency_id, quote_asset_symbol)] = quote_asset
        cryptocurrency_exchange_market = (
            session.query(CryptocurrencyExchangeMarket)
            .filter_by(
                cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                cryptocurrency_exchange_market_category_id=market_category.id,
                base_asset_id=base_asset.id,
                quote_asset_id=quote_asset.id,
            )
            .one_or_none()
        )
        cryptocurrency_exchange_market_url = market_pair["marketUrl"]
        cryptocurrency_exchange_market_coin_market_cap_id = market_pair["marketId"]
        cryptocurrency_exchange_market_coin_market_cap_date_last_updated = iso_time_string_to_datetime(
            market_pair["lastUpdated"]
        )
        if not cryptocurrency_exchange_market:
            cryptocurrency_exchange_market = CryptocurrencyExchangeMarket(
                source_id=coin_market_cap_id,
                cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                cryptocurrency_exchange_market_category_id=market_category.id,
                base_asset_id=base_asset.id,
                quote_asset_id=quote_asset.id,
                cryptocurrency_exchange_market_fee_type_id=market_fee_type.id,
                url=cryptocurrency_exchange_market_url,
                coin_market_cap_id=cryptocurrency_exchange_market_coin_market_cap_id,
                coin_market_cap_date_last_updated=cryptocurrency_exchange_market_coin_market_cap_date_last_updated,
            )
            session.add(cryptocurrency_exchange_market)
            session.flush()
        elif (
            cryptocurrency_exchange_market.coin_market_cap_date_last_updated
            < cryptocurrency_exchange_market_coin_market_cap_date_last_updated
        ):
            cryptocurrency_exchange_market.source_id = coin_market_cap_id
            cryptocurrency_exchange_market.cryptocurrency_exchange_market_fee_type_id = market_fee_type.id
            cryptocurrency_exchange_market.market_url = cryptocurrency_exchange_market_url
            cryptocurrency_exchange_market.coin_market_cap_id = cryptocurrency_exchange_market_coin_market_cap_id
            cryptocurrency_exchange_market.coin_market_cap_date_last_updated = (
                cryptocurrency_exchange_market_coin_market_cap_date_last_updated
            )
            cryptocurrency_exchange_market.is_active = True
        elif not cryptocurrency_exchange_market.is_active:
            cryptocurrency_exchange_market.is_active = True
        cryptocurrency_exchange_market_stat = CryptocurrencyExchangeMarketStat(
            cryptocurrency_exchange_market_stat_pull_id=market_stat_pull.id,
            cryptocurrency_exchange_market_id=cryptocurrency_exchange_market.id,
            price=market_pair["price"],
            usd_volume_24h=market_pair["volumeUsd"],
            base_asset_volume_24h=market_pair["volumeBase"],
            quote_asset_volume_24h=market_pair["volumeQuote"],
            usd_depth_negative_two=market_pair.get("depthUsdNegativeTwo"),
            usd_depth_positive_two=market_pair.get("depthUsdPositiveTwo"),
            source_score=market_pair["marketScore"],
            source_liquidity_score=market_pair["effectiveLiquidity"],
            source_reputation=market_pair["marketReputation"],
            source_outlier_detected=bool(market_pair["outlierDetected"]),
            source_price_excluded=bool(market_pair["priceExcluded"]),
            source_volume_excluded=bool(market_pair["volumeExcluded"]),
        )
        session.add(cryptocurrency_exchange_market_stat)
    session.commit()


@app.task
def queue_update_cryptocurrency_exchange_market_stats_from_coin_market_cap(synchronous: bool = False) -> None:
    if synchronous:
        function = update_cryptocurrency_exchange_market_stats_from_coin_market_cap.apply
        kwargs = {}
    else:
        function = update_cryptocurrency_exchange_market_stats_from_coin_market_cap.apply_async
        kwargs = {"priority": 1}
    enabled_cryptocurrency_exchanges = session.query(EnabledCryptocurrencyExchange).filter_by(is_disabled=False).all()
    for enabled_cryptocurrency_exchange in enabled_cryptocurrency_exchanges:
        if enabled_cryptocurrency_exchange.coin_market_cap_slug:
            function(args=(enabled_cryptocurrency_exchange.cryptocurrency_exchange.id), **kwargs)
