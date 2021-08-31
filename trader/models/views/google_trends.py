from textwrap import dedent
from trader.models.google_trends import (
    GoogleTrends,
    GoogleTrendsKeyword,
    GoogleTrendsPull,
    GoogleTrendsPullGeo,
    GoogleTrendsPullGprop,
    GoogleTrendsPullStep,
)
from trader.models.timeframe import Timeframe


GOOGLE_TRENDS_SQL = dedent(
    """
    CREATE OR REPLACE VIEW public.google_trends_view AS
    SELECT
        g.id AS google_trends_id
        ,g.data_date
        ,g.value
        ,g.is_partial
        ,g.google_trends_keyword_id
        ,k.keyword
        ,ps.timeframe_id AS pull_step_timeframe_id
        ,t1.base_label AS pull_step_timeframe_label
        ,ps.from_date
        ,ps.to_date
        ,ps.is_current
        ,ps.google_trends_pull_id
        ,p.google_trends_pull_geo_id
        ,geo.code AS google_trends_geo_code
        ,geo.name AS google_trends_geo_name
        ,p.google_trends_pull_gprop_id
        ,gprop.code AS google_trends_gprop_code
        ,gprop.name AS google_trends_gprop_name
        ,p.timeframe_id AS pull_timeframe_id
        ,t2.base_label AS pull_timeframe_label
        ,p.from_inclusive
        ,p.to_exclusive
    FROM public.{google_trends_table} g
        INNER JOIN public.{google_trends_keyword_table} k ON
            g.google_trends_keyword_id = k.id
        INNER JOIN public.{google_trends_pull_step_table} ps ON
            g.google_trends_pull_step_id = ps.id
        INNER JOIN public.{timeframe_table} t1 ON
            ps.timeframe_id = t1.id
        INNER JOIN public.{google_trends_pull_table} p ON
            ps.google_trends_pull_id = p.id
        INNER JOIN public.{google_trends_pull_geo_table} geo ON
            p.google_trends_pull_geo_id = geo.id
        INNER JOIN public.{google_trends_pull_gprop_table} gprop ON
            p.google_trends_pull_gprop_id = gprop.id
        INNER JOIN public.{timeframe_table} t2 ON
            p.timeframe_id = t2.id
    """.format(
        google_trends_table=GoogleTrends.__tablename__,
        google_trends_keyword_table=GoogleTrendsKeyword.__tablename__,
        google_trends_pull_step_table=GoogleTrendsPullStep.__tablename__,
        timeframe_table=Timeframe.__tablename__,
        google_trends_pull_table=GoogleTrendsPull.__tablename__,
        google_trends_pull_geo_table=GoogleTrendsPullGeo.__tablename__,
        google_trends_pull_gprop_table=GoogleTrendsPullGprop.__tablename__,
    )
).strip()
