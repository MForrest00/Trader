from textwrap import dedent
from trader.connections.cache import cache
from trader.data.base import STANDARD_CURRENCY
from trader.models.currency import Currency, CurrencyType
from trader.models.standard_currency import StandardCurrency


STANDARD_CURRENCY_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.standard_currency_view AS
    SELECT
        c.id AS currency_id
        ,c.name
        ,c.symbol
        ,sc.id AS standard_currency_id
        ,sc.iso_numeric_code
        ,sc.minor_unit
    FROM public.{currency_table} c
        INNER JOIN public.{currency_type_table} ct ON
            c.currency_type_id = ct.id
        INNER JOIN public.{standard_currency_table} sc ON
            c.id = sc.currency_id
    WHERE
        ct.id = :standard_currency_currency_type_id
    """.format(
        currency_table=Currency.__tablename__,
        currency_type_table=CurrencyType.__tablename__,
        standard_currency_table=StandardCurrency.__tablename__,
    )
).strip()


STANDARD_CURRENCY_PARAMS = {"standard_currency_currency_type_id": int(cache.get(STANDARD_CURRENCY.cache_key).decode())}
