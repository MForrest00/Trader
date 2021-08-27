from textwrap import dedent
from trader.connections.cache import cache
from trader.data.base import CRYPTOCURRENCY
from trader.models.cryptocurrency import Cryptocurrency, CryptocurrencyPlatform
from trader.models.currency import Currency, CurrencyType


CRYPTOCURRENCY_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.crypotocurrency_view AS
    SELECT
        c1.id AS currency_id
        ,c1.name
        ,c1.symbol
        ,c2.id AS cryptocurrency_id
        ,c2.max_supply
        ,c2.source_entity_id
        ,c2.source_slug
        ,c2.source_date_added
        ,c2.source_date_last_updated
        ,cp.id AS cryptocurrency_platform_id
        ,cp.name AS cryptocurrency_platform_name
        ,cp.symbol AS cryptocurrency_platform_symbol
        ,cp.source_entity_id AS cryptocurrency_platform_source_entity_id
        ,cp.source_slug AS cryptocurrency_platform_source_slug
    FROM public.{currency_table} c1
        INNER JOIN public.{currency_type_table} ct ON
            c1.currency_type_id = ct.id
        INNER JOIN public.{cryptocurrency_table} c2 ON
            c1.id = c2.currency_id
        LEFT JOIN public.{cryptocurrency_platform_table} cp ON
            c2.cryptocurrency_platform_id = cp.id
    WHERE
        ct.id = :cryptocurrency_currency_type_id
    """.format(
        currency_table=Currency.__tablename__,
        currency_type_table=CurrencyType.__tablename__,
        cryptocurrency_table=Cryptocurrency.__tablename__,
        cryptocurrency_platform_table=CryptocurrencyPlatform.__tablename__,
    )
).strip()


CRYPTOCURRENCY_PARAMS = {"cryptocurrency_currency_type_id": int(cache.get(CRYPTOCURRENCY.cache_key).decode())}
