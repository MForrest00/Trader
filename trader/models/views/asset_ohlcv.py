from textwrap import dedent
from trader.models.asset import Asset, AssetType
from trader.models.asset_ohlcv import AssetOHLCV, AssetOHLCVGroup, AssetOHLCVPull
from trader.models.source import Source
from trader.models.timeframe import Timeframe


ASSET_OHLCV_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.asset_ohlcv_view AS
    SELECT
        a.id AS asset_ohlcv_id
        ,a.date_open
        ,a.open
        ,a.high
        ,a.low
        ,a.close
        ,a.volume
        ,a.date_high
        ,a.date_low
        ,ap.asset_ohlcv_group_id
        ,ag.source_id
        ,s.name AS source_name
        ,ag.base_asset_id
        ,ba.name AS base_asset_name
        ,ba.symbol AS base_asset_symbol
        ,bat.description AS base_asset_type_description
        ,ag.quote_asset_id
        ,qa.name AS quote_asset_name
        ,qa.symbol AS quote_asset_symbol
        ,qat.description AS quote_asset_type_description
        ,ag.timeframe_id
        ,t.base_label AS timeframe_label
        ,a.asset_ohlcv_pull_id
        ,ap.from_inclusive
        ,ap.to_exclusive
    FROM public.{asset_ohlcv_table} a
        INNER JOIN public.{asset_ohlcv_pull_table} ap ON
            a.asset_ohlcv_pull_id = ap.id
        INNER JOIN public.{asset_ohlcv_group_table} ag ON
            ap.asset_ohlcv_group_id = ag.id
        INNER JOIN public.{source_table} s ON
            ag.source_id = s.id
        INNER JOIN public.{asset_table} ba ON
            ag.base_asset_id = ba.id
        INNER JOIN public.{asset_type_table} bat ON
            ba.asset_type_id = bat.id
        INNER JOIN public.{asset_table} qa ON
            ag.quote_asset_id = qa.id
        INNER JOIN public.{asset_type_table} qat ON
            qa.asset_type_id = qat.id
        INNER JOIN public.{timeframe_table} t ON
            ag.timeframe_id = t.id
    """.format(
        asset_ohlcv_table=AssetOHLCV.__tablename__,
        asset_ohlcv_pull_table=AssetOHLCVPull.__tablename__,
        asset_ohlcv_group_table=AssetOHLCVGroup.__tablename__,
        source_table=Source.__tablename__,
        asset_table=Asset.__tablename__,
        asset_type_table=AssetType.__tablename__,
        timeframe_table=Timeframe.__tablename__,
    )
).strip()
