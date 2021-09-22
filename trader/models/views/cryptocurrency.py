from textwrap import dedent
from trader.data.base import ASSET_TYPE_CRYPTOCURRENCY
from trader.models.asset import Asset, AssetType
from trader.models.cryptocurrency import Cryptocurrency, CryptocurrencyPlatform


CRYPTOCURRENCY_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.cryptocurrency_view AS
    SELECT
        a.id AS asset_id
        ,a.name
        ,a.symbol
        ,c.id AS cryptocurrency_id
        ,c.max_supply
        ,c.source_entity_id
        ,c.source_slug
        ,c.source_date_added
        ,c.source_date_last_updated
        ,cp.id AS cryptocurrency_platform_id
        ,cp.name AS cryptocurrency_platform_name
        ,cp.symbol AS cryptocurrency_platform_symbol
        ,cp.source_entity_id AS cryptocurrency_platform_source_entity_id
        ,cp.source_slug AS cryptocurrency_platform_source_slug
    FROM public.{asset_table} a
        INNER JOIN public.{asset_type_table} at ON
            a.asset_type_id = at.id
        INNER JOIN public.{cryptocurrency_table} c ON
            a.id = c.currency_id
        LEFT JOIN public.{cryptocurrency_platform_table} cp ON
            c2.cryptocurrency_platform_id = cp.id
    WHERE
        at.description = '{cryptocurrency_description}'
    """.format(
        asset_table=Asset.__tablename__,
        asset_type_table=AssetType.__tablename__,
        cryptocurrency_table=Cryptocurrency.__tablename__,
        cryptocurrency_platform_table=CryptocurrencyPlatform.__tablename__,
        cryptocurrency_description=ASSET_TYPE_CRYPTOCURRENCY.description,
    )
).strip()
