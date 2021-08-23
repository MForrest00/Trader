from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Sequence, Tuple, Union
from dateutil.relativedelta import relativedelta
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.connections.trend_request import trend_request
from trader.data.base import EIGHT_MINUTE, GOOGLE_TRENDS, ONE_DAY, ONE_MINUTE, ONE_MONTH, WEB_SEARCH
from trader.models.google_trends import (
    GoogleTrends,
    GoogleTrendsKeyword,
    GoogleTrendsPull,
    GoogleTrendsPullGoogleTrendsKeyword,
    GoogleTrendsPullStep,
    GoogleTrendsPullGeo,
    GoogleTrendsPullGprop,
)
from trader.models.timeframe import Timeframe
from trader.utilities.constants import (
    GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE,
    GOOGLE_TRENDS_OTHER_SEARCH_MINUTE_GRANULARITY_CUTOFF,
    GOOGLE_TRENDS_TIMEFRAME_RANKS,
    GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE,
    GOOGLE_TRENDS_WEB_SEARCH_MINUTE_GRANULARITY_CUTOFF,
)
from trader.utilities.functions import TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION


def timeframe_base_label_to_date_ranges(
    timeframe_base_label: str,
    gprop: GoogleTrendsPullGprop,
    from_inclusive: Optional[datetime],
    to_exclusive: Optional[datetime],
) -> List[Tuple[datetime, Optional[datetime]]]:
    if timeframe_base_label == ONE_MONTH.base_label:
        if gprop.name == WEB_SEARCH.name:
            return [(GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE, None)]
        return [(GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE, None)]
    if not from_inclusive:
        from_inclusive = (
            GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE
            if gprop.name == WEB_SEARCH.name
            else GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE
        )
    if not to_exclusive:
        to_exclusive = datetime.now(timezone.utc)
    if not from_inclusive < to_exclusive:
        raise ValueError("From argument must be less than the to argument")
    minute_granularity_cutoff = (
        GOOGLE_TRENDS_WEB_SEARCH_MINUTE_GRANULARITY_CUTOFF
        if gprop.name == WEB_SEARCH.name
        else GOOGLE_TRENDS_OTHER_SEARCH_MINUTE_GRANULARITY_CUTOFF
    )
    output: List[Tuple[datetime, Optional[datetime]]] = []
    if timeframe_base_label == ONE_DAY.base_label:
        from_val = TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION["M"](from_inclusive)
        while from_val < to_exclusive:
            to_val = (from_val + relativedelta(months=1)) - timedelta(days=1)
            output.append((from_val, to_val))
            from_val += relativedelta(months=1)
    if timeframe_base_label == EIGHT_MINUTE.base_label:
        from_val = max(TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION["d"](from_inclusive), minute_granularity_cutoff)
        while from_val < to_exclusive:
            to_val = from_val + timedelta(days=1)
            output.append((from_val, to_val))
            from_val = to_val
    if timeframe_base_label == ONE_MINUTE.base_label:
        from_val = max(TIMEFRAME_UNIT_TO_TRANSFORM_FUNCTION["h"](from_inclusive), minute_granularity_cutoff)
        from_val -= timedelta(seconds=60 * 60 * (from_val.hour % 4))
        while from_val < to_exclusive:
            to_val = from_val + timedelta(seconds=60 * 60 * 4)
            output.append((from_val, to_val))
            from_val = to_val
    return output


def date_range_to_timeframe_string(
    from_inclusive: datetime, to_exclusive: Optional[datetime]
) -> Tuple[str, Optional[str]]:
    if from_inclusive == GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE and to_exclusive is None:
        return "all", None
    if from_inclusive == GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE and to_exclusive is None:
        return "all_2008", None
    if to_exclusive is None:
        raise ValueError("From and to arguments do not reflect a timeframe compatible with Google Trends")
    from_inclusive_string = from_inclusive.strftime("%Y-%m-%d")
    to_exclusive_string = to_exclusive.strftime("%Y-%m-%d")
    if (to_exclusive - from_inclusive) <= timedelta(days=1):
        return f"{from_inclusive_string}T00", f"{to_exclusive_string}T00"
    return from_inclusive_string, to_exclusive_string


def retrieve_interest_over_time_from_google_trends(
    keywords: Sequence[str],
    geo: GoogleTrendsPullGeo,
    gprop: GoogleTrendsPullGprop,
    timeframe_string: str,
) -> Tuple[Timeframe, List[Dict[str, Union[datetime, int, bool]]]]:
    trend_request.build_payload(keywords, timeframe=timeframe_string, geo=geo.code, gprop=gprop.code)
    data = trend_request.interest_over_time().to_dict("index")
    output: List[Dict[str, Union[datetime, int, bool]]] = []
    for time, columns in data.items():
        item_data = {"time": time.to_pydatetime().replace(tzinfo=timezone.utc)}
        item_data.update(columns)
        output.append(item_data)
    return sorted(output, key=lambda x: x["time"])


def update_interest_over_time_from_google_trends(
    keywords: Sequence[str],
    geo: GoogleTrendsPullGeo,
    gprop: GoogleTrendsPullGprop,
    from_inclusive: Optional[datetime],
    to_exclusive: Optional[datetime],
    timeframe: Timeframe,
) -> None:
    google_trends_id = int(cache.get(GOOGLE_TRENDS.cache_key).decode())
    try:
        target_timeframe_rank = GOOGLE_TRENDS_TIMEFRAME_RANKS.index(timeframe.base_label)
    except ValueError as error:
        raise ValueError("Timeframe was not a compatible value for Google Trends") from error
    keywords = [keyword.lower() for keyword in keywords]
    keyword_to_google_trends_keyword: Dict[str, GoogleTrendsKeyword] = {}
    with DBSession() as session:
        for keyword_string in keywords:
            keyword = session.query(GoogleTrendsKeyword).filter_by(keyword=keyword_string).one_or_none()
            if not keyword:
                keyword = GoogleTrendsKeyword(keyword=keyword_string)
                session.add(keyword)
                session.flush()
            keyword_to_google_trends_keyword[keyword_string] = keyword
        keyword_id_set = set(k.id for k in keyword_to_google_trends_keyword.values())
        google_trends_pull = GoogleTrendsPull(
            source_id=google_trends_id,
            google_trends_pull_geo_id=geo.id,
            google_trends_pull_gprop_id=gprop.id,
            timeframe_id=timeframe.id,
            from_inclusive=from_inclusive,
            to_exclusive=to_exclusive,
        )
        session.add(google_trends_pull)
        session.flush()
        for keyword in keywords:
            google_trends_pull_google_trends_keyword = GoogleTrendsPullGoogleTrendsKeyword(
                google_trends_pull_id=google_trends_pull.id,
                google_trends_keyword=keyword_to_google_trends_keyword[keyword].id,
            )
            session.add(google_trends_pull_google_trends_keyword)
        for timeframe_base_label in reversed(GOOGLE_TRENDS_TIMEFRAME_RANKS[target_timeframe_rank:]):
            date_ranges = timeframe_base_label_to_date_ranges(timeframe_base_label, gprop, from_inclusive, to_exclusive)
            if date_ranges:
                timeframe = session.query(Timeframe).filter_by(base_label=timeframe_base_label).one_or_none()
                for from_val, to_val in date_ranges:
                    from_string, to_string = date_range_to_timeframe_string(from_val, to_val)
                    competing_google_trends_pull_steps = (
                        session.query(GoogleTrendsPullStep)
                        .join(GoogleTrendsPull)
                        .filter(
                            GoogleTrendsPullStep.timeframe_id == timeframe.id,
                            GoogleTrendsPullStep.from_string == from_string,
                            GoogleTrendsPullStep.to_string == to_string,
                            GoogleTrendsPullStep.is_current.is_(True),
                            GoogleTrendsPull.google_trends_pull_geo_id == geo.id,
                            GoogleTrendsPull.google_trends_pull_gprop_id == gprop.id,
                        )
                    )
                    for competing_google_trends_pull_step in competing_google_trends_pull_steps:
                        google_trends_pull = competing_google_trends_pull_step.google_trends_pull
                        google_trends_pull_keywords = google_trends_pull.google_trends_pull_google_trends_keywords
                        google_trends_pull_keyword_ids = set(
                            k.google_trends_keyword.id for k in google_trends_pull_keywords
                        )
                        if google_trends_pull_keyword_ids == keyword_id_set:
                            competing_google_trends_pull_step.is_current = False
                    google_trends_pull_step = GoogleTrendsPullStep(
                        google_trends_pull_id=google_trends_pull.id,
                        timeframe_id=timeframe.id,
                        from_string=from_string,
                        to_string=to_string,
                    )
                    session.add(google_trends_pull_step)
                    session.flush()
                    timeframe_string = from_string if to_string is None else f"{from_string} {to_string}"
                    data = retrieve_interest_over_time_from_google_trends(keywords, geo, gprop, timeframe_string)
                    if timeframe_base_label[-1] == "m":
                        data = data[:-1]
                    for record in data:
                        data_date = record.pop("time")
                        is_partial = bool(record.pop("isPartial"))
                        for keyword, value in record.items():
                            keyword_id = keyword_to_google_trends_keyword[keyword].id
                            google_trends = GoogleTrends(
                                google_trends_pull_step_id=google_trends_pull_step.id,
                                google_trends_keyword_id=keyword_id,
                                data_date=data_date,
                                value=value,
                                is_partial=is_partial,
                            )
                            session.add(google_trends)
                    session.commit()
