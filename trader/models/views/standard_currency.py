from textwrap import dedent
from trader.data.initial.asset_type import ASSET_TYPE_STANDARD_CURRENCY
from trader.models.asset import Asset, AssetType
from trader.models.standard_currency import StandardCurrency


STANDARD_CURRENCY_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.standard_currency_view AS
    SELECT
        a.id AS asset_id
        ,a.name
        ,a.symbol
        ,sc.id AS standard_currency_id
        ,sc.iso_numeric_code
        ,sc.minor_unit
    FROM public.{asset_table} a
        INNER JOIN public.{asset_type_table} at ON
            a.asset_type_id = at.id
        INNER JOIN public.{standard_currency_table} sc ON
            a.id = sc.asset_id
    WHERE
        at.description = '{standard_currency_description}'
    """.format(
        asset_table=Asset.__tablename__,
        asset_type_table=AssetType.__tablename__,
        standard_currency_table=StandardCurrency.__tablename__,
        standard_currency_description=ASSET_TYPE_STANDARD_CURRENCY.description,
    )
).strip()
