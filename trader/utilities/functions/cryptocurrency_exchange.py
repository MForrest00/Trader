from typing import Set, Sequence
from trader.connections.database import session
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import CryptocurrencyExchangeMarket
from trader.models.enabled_quote_asset import EnabledQuoteAsset


def fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges(
    cryptocurrency_exchanges: Sequence[CryptocurrencyExchange],
) -> Set[int]:
    enabled_quote_assets = session.query(EnabledQuoteAsset).all()
    enabled_quote_asset_ids = [c.asset.id for c in enabled_quote_assets if c.history[0].is_enabled]
    base_asset_ids: Set[int] = set()
    for cryptocurrency_exchange in cryptocurrency_exchanges:
        markets = (
            session.query(CryptocurrencyExchangeMarket)
            .filter(
                CryptocurrencyExchangeMarket.cryptocurrency_exchange_id == cryptocurrency_exchange.id,
                CryptocurrencyExchangeMarket.quote_asset_id.in_(enabled_quote_asset_ids),
                CryptocurrencyExchangeMarket.is_active.is_(True),
            )
            .all()
        )
        for market in markets:
            base_asset_ids.add(market.base_asset_id)
    return base_asset_ids
