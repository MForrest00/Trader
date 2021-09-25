from typing import Set, Sequence
from sqlalchemy.orm import Session
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import CryptocurrencyExchangeMarket
from trader.models.enabled_quote_asset import EnabledQuoteAsset


def fetch_enabled_base_asset_ids_for_cryptocurrency_exchanges(
    session: Session, cryptocurrency_exchanges: Sequence[CryptocurrencyExchange]
) -> Set[int]:
    enabled_quote_assets = session.query(EnabledQuoteAsset).filter_by(is_disabled=False).all()
    enabled_quote_asset_ids = [c.asset.id for c in enabled_quote_assets]
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
