from textwrap import dedent
from trader.models.google_trends import (
    GoogleTrends,
    GoogleTrendsGeo,
    GoogleTrendsGprop,
    GoogleTrendsGroup,
    GoogleTrendsKeywords,
    GoogleTrendsPull,
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
        ,k.keywords[g.google_trends_keyword_index] AS keyword
        ,g.google_trends_pull_step_id
        ,ps.timeframe_id AS google_trends_pull_step_timeframe_id
        ,t1.base_label AS google_trends_pull_step_timeframe_label
        ,ps.from_date
        ,ps.to_date
        ,ps.is_current
        ,ps.google_trends_pull_id
        ,p.google_trends_group_id
        ,gr.google_trends_geo_id
        ,geo.code AS google_trends_geo_code
        ,geo.name AS google_trends_geo_name
        ,gr.google_trends_gprop_id
        ,gprop.code AS google_trends_gprop_code
        ,gprop.name AS google_trends_gprop_name
        ,gr.google_trends_keywords_id
        ,k.keywords AS google_trends_keywords
        ,gr.timeframe_id AS google_trends_group_timeframe_id
        ,t2.base_label AS google_trends_group_timeframe_label
        ,p.from_inclusive
        ,p.to_exclusive
    FROM public.{google_trends_table} g
        INNER JOIN public.{google_trends_pull_step_table} ps ON
            g.google_trends_pull_step_id = ps.id
        INNER JOIN public.{timeframe_table} t1 ON
            ps.timeframe_id = t1.id
        INNER JOIN public.{google_trends_pull_table} p ON
            ps.google_trends_pull_id = p.id
        INNER JOIN public.{google_trends_group_table} gr ON
            p.google_trends_group_id = gr.id
        INNER JOIN public.{google_trends_geo_table} geo ON
            gr.google_trends_geo_id = geo.id
        INNER JOIN public.{google_trends_gprop_table} gprop ON
            gr.google_trends_gprop_id = gprop.id
        INNER JOIN public.{google_trends_keywords_table} k ON
            gr.google_trends_keywords_id = k.id
        INNER JOIN public.{timeframe_table} t2 ON
            gr.timeframe_id = t2.id
    """.format(
        google_trends_table=GoogleTrends.__tablename__,
        google_trends_pull_step_table=GoogleTrendsPullStep.__tablename__,
        google_trends_pull_table=GoogleTrendsPull.__tablename__,
        google_trends_group_table=GoogleTrendsGroup.__tablename__,
        google_trends_geo_table=GoogleTrendsGeo.__tablename__,
        google_trends_gprop_table=GoogleTrendsGprop.__tablename__,
        google_trends_keywords_table=GoogleTrendsKeywords.__tablename__,
        timeframe_table=Timeframe.__tablename__,
    )
).strip()
