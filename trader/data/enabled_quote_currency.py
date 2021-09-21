from trader.connections.database import DBSession
from trader.data.base import CURRENCY_TYPE_CRYPTOCURRENCY, CURRENCY_TYPE_STANDARD_CURRENCY
from trader.models.currency import Currency
from trader.models.enabled_quote_currency import EnabledQuoteCurrency
from trader.utilities.constants import INITIAL_ENABLED_QUOTE_CRYPTOCURRENCIES, INITIAL_ENABLED_QUOTE_STANDARD_CURRENCIES
from trader.utilities.functions import fetch_base_data_id


def set_initial_enabled_quote_currencies() -> None:
    with DBSession() as session:
        for enabled_quote_currency in INITIAL_ENABLED_QUOTE_CRYPTOCURRENCIES:
            cryptocurrency = (
                session.query(Currency)
                .filter_by(
                    currency_type_id=fetch_base_data_id(CURRENCY_TYPE_CRYPTOCURRENCY),
                    symbol=enabled_quote_currency.symbol,
                )
                .one_or_none()
            )
            if cryptocurrency:
                if not cryptocurrency.enabled_quote_currency:
                    enabled_quote_cryptocurrency = EnabledQuoteCurrency(
                        currency_id=cryptocurrency.id, priority=enabled_quote_currency.priority
                    )
                    session.add(enabled_quote_cryptocurrency)
        for enabled_quote_currency in INITIAL_ENABLED_QUOTE_STANDARD_CURRENCIES:
            standard_currency = (
                session.query(Currency)
                .filter_by(
                    currency_type_id=fetch_base_data_id(CURRENCY_TYPE_STANDARD_CURRENCY),
                    symbol=enabled_quote_currency.symbol,
                )
                .one_or_none()
            )
            if standard_currency:
                if not standard_currency.enabled_quote_currency:
                    enabled_quote_standard_currency = EnabledQuoteCurrency(
                        currency_id=standard_currency.id, priority=enabled_quote_currency.priority
                    )
                    session.add(enabled_quote_standard_currency)
        session.commit()
