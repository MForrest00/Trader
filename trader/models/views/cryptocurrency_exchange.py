from textwrap import dedent
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange, CryptocurrencyExchangeType
from trader.models.source import Source, SourceType


CRYPTOCURRENCY_EXCHANGE_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.cryptocurrency_exchange_view AS
    SELECT
        s.id AS source_id
        ,s.name
        ,ct.description AS cryptocurrency_exchange_type_description
        ,c.date_launched
        ,c.coin_market_cap_id
        ,c.coin_market_cap_slug
        ,c.coin_market_cap_date_last_updated
    FROM public.{source_table} s
        INNER JOIN public.{source_type_table} st ON
            s.source_type_id = st.id
        INNER JOIN public.{cryptocurrency_exchange_table} c ON
            s.id = c.source_id
        LEFT JOIN public.{cryptocurrency_exchange_type_table} ct ON
            c.cryptocurrency_exchange_type_id = ct.id
    WHERE
        st.description = 'Cryptocurrency exchange'
    """.format(
        source_table=Source.__tablename__,
        source_type_table=SourceType.__tablename__,
        cryptocurrency_exchange_table=CryptocurrencyExchange.__tablename__,
        cryptocurrency_exchange_type_table=CryptocurrencyExchangeType.__tablename__,
    )
).strip()
