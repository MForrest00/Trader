from textwrap import dedent
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.cryptocurrency_exchange_market import (
    CryptocurrencyExchangeMarket,
    CryptocurrencyExchangeMarketCategory,
    CryptocurrencyExchangeMarketFeeType,
)
from trader.models.currency import Currency, CurrencyType
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
        ,cem.base_currency_id
        ,bc.name AS base_currency_name
        ,bc.symbol AS base_currency_symbol
        ,bct.description AS base_currency_type_description
        ,cem.quote_currency_id
        ,qc.name AS quote_currency_name
        ,qc.symbol AS quote_currency_symbol
        ,qct.description AS quote_currency_type_description
        ,cem.cryptocurrency_exchange_market_fee_type_id
        ,cemft.description AS cryptocurrency_exchange_market_fee_type_description
        ,cem.market_url
        ,cem.source_entity_id
        ,cem.source_date_last_updated
    FROM public.{cryptocurrency_exchange_market_table} cem
        INNER JOIN public.{cryptocurrency_exchange_table} ce ON
            cem.cryptocurrency_exchange_id = ce.id
        INNER JOIN public.{source_table} s ON
            ce.source_id = s.id
        INNER JOIN {cryptocurrency_exchange_market_category_table} cemc ON
            cem.cryptocurrency_exchange_market_category_id = cemc.id
        INNER JOIN public.{currency_table} bc ON
            cem.base_currency_id = bc.id
        INNER JOIN public.{currency_type_table} bct ON
            bc.currency_type_id = bct.id
        INNER JOIN public.{currency_table} qc ON
            cem.quote_currency_id = qc.id
        INNER JOIN public.{currency_type_table} qct ON
            qc.currency_type_id = qct.id
        INNER JOIN public.{cryptocurrency_exchange_market_fee_type_table} cemft ON
            cem.cryptocurrency_exchange_market_fee_type_id = cemft.id
    """.format(
        cryptocurrency_exchange_market_table=CryptocurrencyExchangeMarket.__tablename__,
        cryptocurrency_exchange_table=CryptocurrencyExchange.__tablename__,
        source_table=Source.__tablename__,
        cryptocurrency_exchange_market_category_table=CryptocurrencyExchangeMarketCategory.__tablename__,
        currency_table=Currency.__tablename__,
        currency_type_table=CurrencyType.__tablename__,
        cryptocurrency_exchange_market_fee_type_table=CryptocurrencyExchangeMarketFeeType.__tablename__,
    )
).strip()
