from textwrap import dedent
from trader.models.currency import Currency, CurrencyType
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVPull
from trader.models.timeframe import Timeframe


CURRENCY_OHLCV_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.currency_ohlcv_view AS
    SELECT
        c.id AS currency_ohlcv_id
        ,c.date_open
        ,c.open
        ,c.high
        ,c.low
        ,c.close
        ,c.volume
        ,c.date_high
        ,c.date_low
        ,c.currency_ohlcv_pull_id
        ,cp.base_currency_id
        ,bc.name AS base_currency_name
        ,bc.symbol AS base_currency_symbol
        ,bct.description AS base_currency_type_description
        ,cp.quote_currency_id
        ,qc.name AS quote_currency_name
        ,qc.symbol AS quote_currency_symbol
        ,qct.description AS quote_currency_type_description
        ,cp.timeframe_id
        ,t.base_label AS timeframe_label
        ,cp.from_inclusive
        ,cp.to_exclusive
    FROM public.{currency_ohlcv_table} c
        INNER JOIN public.{currency_ohlcv_pull_table} cp ON
            c.currency_ohlcv_pull_id = cp.id
        INNER JOIN public.{currency_table} bc ON
            cp.base_currency_id = bc.id
        INNER JOIN public.{currency_type_table} bct ON
            bc.currency_type_id = bct.id
        INNER JOIN public.{currency_table} qc ON
            cp.quote_currency_id = qc.id
        INNER JOIN public.{currency_type_table} qct ON
            qc.currency_type_id = qct.id
        INNER JOIN public.{timeframe_table} t ON
            cp.timeframe_id = t.id
    """.format(
        currency_ohlcv_table=CurrencyOHLCV.__tablename__,
        currency_ohlcv_pull_table=CurrencyOHLCVPull.__tablename__,
        currency_table=Currency.__tablename__,
        currency_type_table=CurrencyType.__tablename__,
        timeframe_table=Timeframe.__tablename__,
    )
).strip()