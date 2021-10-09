from textwrap import dedent
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import (
    CryptocurrencyExchangeMarket,
    CryptocurrencyExchangeMarketCategory,
    CryptocurrencyExchangeMarketFeeType,
)
from trader.models.asset import Asset, AssetType
from trader.models.source import Source


CRYPTOCURRENCY_EXCHANGE_MARKET_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.cryptocurrency_exchange_market_view AS
    SELECT
        cem.id AS cryptocurrency_exchange_market_id
        ,cem.cryptocurrency_exchange_id
        ,s.name cryptocurrency_exchange_name
        ,cem.cryptocurrency_exchange_market_category_id
        ,cemc.description AS cryptocurrency_exchange_market_category_description
        ,cem.base_asset_id
        ,ba.name AS base_asset_name
        ,ba.symbol AS base_asset_symbol
        ,bat.description AS base_asset_type_description
        ,cem.quote_asset_id
        ,qa.name AS quote_asset_name
        ,qa.symbol AS quote_asset_symbol
        ,qat.description AS quote_asset_type_description
        ,cem.cryptocurrency_exchange_market_fee_type_id
        ,cemft.description AS cryptocurrency_exchange_market_fee_type_description
        ,cem.url
        ,cem.coin_market_cap_id
        ,cem.coin_market_cap_date_last_updated
    FROM public.{cryptocurrency_exchange_market_table} cem
        INNER JOIN public.{cryptocurrency_exchange_table} ce ON
            cem.cryptocurrency_exchange_id = ce.id
        INNER JOIN public.{source_table} s ON
            ce.source_id = s.id
        INNER JOIN {cryptocurrency_exchange_market_category_table} cemc ON
            cem.cryptocurrency_exchange_market_category_id = cemc.id
        INNER JOIN public.{asset_table} ba ON
            cem.base_asset_id = ba.id
        INNER JOIN public.{asset_type_table} bat ON
            ba.asset_type_id = bat.id
        INNER JOIN public.{asset_table} qa ON
            cem.quote_asset_id = qa.id
        INNER JOIN public.{asset_type_table} qat ON
            qa.asset_type_id = qat.id
        INNER JOIN public.{cryptocurrency_exchange_market_fee_type_table} cemft ON
            cem.cryptocurrency_exchange_market_fee_type_id = cemft.id
    """.format(
        cryptocurrency_exchange_market_table=CryptocurrencyExchangeMarket.__tablename__,
        cryptocurrency_exchange_table=CryptocurrencyExchange.__tablename__,
        source_table=Source.__tablename__,
        cryptocurrency_exchange_market_category_table=CryptocurrencyExchangeMarketCategory.__tablename__,
        asset_table=Asset.__tablename__,
        asset_type_table=AssetType.__tablename__,
        cryptocurrency_exchange_market_fee_type_table=CryptocurrencyExchangeMarketFeeType.__tablename__,
    )
).strip()
