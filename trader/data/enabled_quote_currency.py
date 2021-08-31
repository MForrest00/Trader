from trader.connections.database import DBSession
from trader.data.base import CRYPTOCURRENCY, STANDARD_CURRENCY
from trader.models.currency import Currency
from trader.models.enabled_quote_currency import EnabledQuoteCurrency
from trader.utilities.constants import INITIAL_ENABLED_QUOTE_CRYPTOCURRENCY_SYMBOLS, INITIAL_ENABLED_QUOTE_STANDARD_CURRENCY_SYMBOLS
from trader.utilities.functions import fetch_base_data_id


def set_initial_enabled_quote_currencies() -> None:
    cryptocurrency_id = fetch_base_data_id(CRYPTOCURRENCY)
    standard_currency_id = fetch_base_data_id(STANDARD_CURRENCY)
    with DBSession() as session:
        for quote_cryptocurrency_symbol in INITIAL_ENABLED_QUOTE_CRYPTOCURRENCY_SYMBOLS:
            cryptocurrency = (
                session.query(Currency)
                .filter_by(symbol=quote_cryptocurrency_symbol, currency_type_id=cryptocurrency_id)
                .first()
            )
            if cryptocurrency:
                if not cryptocurrency.enabled_quote_currency:
                    enabled_quote_cryptocurrency = EnabledQuoteCurrency(currency_id=cryptocurrency.id)
                    session.add(enabled_quote_cryptocurrency)
        for quote_standard_currency_symbol in INITIAL_ENABLED_QUOTE_STANDARD_CURRENCY_SYMBOLS:
            standard_currency = (
                session.query(Currency)
                .filter_by(symbol=quote_standard_currency_symbol, currency_type_id=standard_currency_id)
                .first()
            )
            if standard_currency:
                if not standard_currency.enabled_quote_currency:
                    enabled_quote_standard_currency = EnabledQuoteCurrency(currency_id=standard_currency.id)
                    session.add(enabled_quote_standard_currency)
        session.commit()