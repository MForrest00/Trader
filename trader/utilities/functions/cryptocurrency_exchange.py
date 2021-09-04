from typing import Set, Sequence
from sqlalchemy.orm import Session
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import CryptocurrencyExchangeMarket
from trader.models.enabled_quote_currency import EnabledQuoteCurrency


def fetch_enabled_base_currency_ids_for_cryptocurrency_exchanges(
    session: Session, cryptocurrency_exchanges: Sequence[CryptocurrencyExchange]
) -> Set[int]:
    enabled_quote_currencies = session.query(EnabledQuoteCurrency).filter_by(is_disabled=False).all()
    enabled_quote_currency_ids = [c.currency.id for c in enabled_quote_currencies]
    base_currency_ids: Set[int] = set()
    for cryptocurrency_exchange in cryptocurrency_exchanges:
        markets = (
            session.query(CryptocurrencyExchangeMarket)
            .filter(
                CryptocurrencyExchangeMarket.cryptocurrency_exchange_id == cryptocurrency_exchange.id,
                CryptocurrencyExchangeMarket.quote_currency_id.in_(enabled_quote_currency_ids),
                CryptocurrencyExchangeMarket.is_active.is_(True),
            )
            .all()
        )
        for market in markets:
            base_currency_ids.add(market.base_currency_id)
    return base_currency_ids
