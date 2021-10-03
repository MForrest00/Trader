from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Sequence, Tuple, Union
from dateutil.relativedelta import relativedelta
from trader.connections.database import session
from trader.connections.trend_request import trend_request
from trader.data.initial.google_trends_gprop import GOOGLE_TRENDS_GPROP_WEB_SEARCH
from trader.data.initial.source import SOURCE_GOOGLE_TRENDS
from trader.data.initial.timeframe import (
    TIMEFRAME_EIGHT_MINUTE,
    TIMEFRAME_ONE_DAY,
    TIMEFRAME_ONE_MINUTE,
    TIMEFRAME_ONE_MONTH,
)
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
from trader.utilities.functions.time import clean_range_cap


GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE = datetime(2004, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_WEB_SEARCH_MINUTE_GRANULARITY_CUTOFF = datetime(2015, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE = datetime(2008, 1, 1, tzinfo=timezone.utc)
GOOGLE_TRENDS_OTHER_SEARCH_MINUTE_GRANULARITY_CUTOFF = datetime(2017, 9, 12, tzinfo=timezone.utc)
GOOGLE_TRENDS_TIMEFRAME_RANKS = (
    TIMEFRAME_ONE_MINUTE.base_label,
    TIMEFRAME_EIGHT_MINUTE.base_label,
    TIMEFRAME_ONE_DAY.base_label,
    TIMEFRAME_ONE_MONTH.base_label,
)


def timeframe_base_label_to_date_ranges(
    timeframe_base_label: str,
    gprop: GoogleTrendsGprop,
    from_inclusive: Optional[datetime],
    to_exclusive: Optional[datetime],
) -> List[Tuple[datetime, Optional[datetime]]]:
    if timeframe_base_label == TIMEFRAME_ONE_MONTH.base_label:
        if gprop.name == GOOGLE_TRENDS_GPROP_WEB_SEARCH.name:
            return [(GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE, None)]
        return [(GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE, None)]
    if not from_inclusive:
        from_inclusive = (
            GOOGLE_TRENDS_WEB_SEARCH_BASE_DATE
            if gprop.name == GOOGLE_TRENDS_GPROP_WEB_SEARCH.name
            else GOOGLE_TRENDS_OTHER_SEARCH_BASE_DATE
        )
    if not to_exclusive:
        to_exclusive = datetime.now(timezone.utc)
    if not from_inclusive < to_exclusive:
        raise ValueError("From argument must be less than the to argument")
    minute_granularity_cutoff = (
        GOOGLE_TRENDS_WEB_SEARCH_MINUTE_GRANULARITY_CUTOFF
        if gprop.name == GOOGLE_TRENDS_GPROP_WEB_SEARCH.name
        else GOOGLE_TRENDS_OTHER_SEARCH_MINUTE_GRANULARITY_CUTOFF
    )
    output: List[Tuple[datetime, Optional[datetime]]] = []
    if timeframe_base_label == TIMEFRAME_ONE_DAY.base_label:
        from_val = clean_range_cap(from_inclusive, "M")
        while from_val < to_exclusive:
            to_val = (from_val + relativedelta(months=1)) - timedelta(days=1)
            output.append((from_val, to_val))
            from_val += relativedelta(months=1)
    if timeframe_base_label == TIMEFRAME_EIGHT_MINUTE.base_label:
        from_val = max(clean_range_cap(from_inclusive, "d"), minute_granularity_cutoff)
        while from_val < to_exclusive:
            to_val = from_val + timedelta(days=1)
            output.append((from_val, to_val))
            from_val = to_val
    if timeframe_base_label == TIMEFRAME_ONE_MINUTE.base_label:
        from_val = max(clean_range_cap(from_inclusive, "h"), minute_granularity_cutoff)
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
    geo: GoogleTrendsGeo,
    gprop: GoogleTrendsGprop,
    timeframe_string: str,
) -> Tuple[Timeframe, List[Dict[str, Union[datetime, int, bool]]]]:
    trend_request.build_payload(keywords, timeframe=timeframe_string, geo=geo.code, gprop=gprop.code)
    data = trend_request.interest_over_time().to_dict("index")
    output: List[Dict[str, Union[datetime, int, bool]]] = []
    for time, columns in data.items():
        item_data = {"data_date": time.to_pydatetime().replace(tzinfo=timezone.utc)}
        item_data.update(columns)
        output.append(item_data)
    return sorted(output, key=lambda x: x["data_date"])


def update_interest_over_time_from_google_trends(
    keywords: Sequence[str],
    geo: GoogleTrendsGeo,
    gprop: GoogleTrendsGprop,
    timeframe: Timeframe,
    from_inclusive: Optional[datetime],
    to_exclusive: Optional[datetime] = None,
) -> None:
    google_trends_id = SOURCE_GOOGLE_TRENDS.fetch_id()
    try:
        target_timeframe_rank = GOOGLE_TRENDS_TIMEFRAME_RANKS.index(timeframe.base_label)
    except ValueError as error:
        raise ValueError("Timeframe was not a compatible value for Google Trends") from error
    keywords = sorted([keyword.lower() for keyword in keywords if keyword])
    if not keywords:
        raise ValueError("Must include a keywords sequence with at least one valid keyword")
    google_trends_keywords = session.query(GoogleTrendsKeywords).filter_by(keywords=keywords).one_or_none()
    if not google_trends_keywords:
        google_trends_keywords = GoogleTrendsKeywords(keywords=keywords)
        session.add(google_trends_keywords)
        session.flush()
    google_trends_group = (
        session.query(GoogleTrendsGroup)
        .filter_by(
            source_id=google_trends_id,
            google_trends_geo_id=geo.id,
            google_trends_gprop_id=gprop.id,
            google_trends_keywords_id=google_trends_keywords.id,
            timeframe_id=timeframe.id,
        )
        .one_or_none()
    )
    if not google_trends_group:
        google_trends_group = GoogleTrendsGroup(
            source_id=google_trends_id,
            google_trends_geo_id=geo.id,
            google_trends_gprop_id=gprop.id,
            google_trends_keywords_id=google_trends_keywords.id,
            timeframe_id=timeframe.id,
        )
        session.add(google_trends_group)
        session.flush()
    google_trends_pull = GoogleTrendsPull(
        google_trends_group_id=google_trends_group.id,
        from_inclusive=from_inclusive,
        to_exclusive=to_exclusive,
    )
    session.add(google_trends_pull)
    session.flush()
    for timeframe_base_label in reversed(GOOGLE_TRENDS_TIMEFRAME_RANKS[target_timeframe_rank:]):
        date_ranges = timeframe_base_label_to_date_ranges(timeframe_base_label, gprop, from_inclusive, to_exclusive)
        if date_ranges:
            timeframe = session.query(Timeframe).filter_by(base_label=timeframe_base_label).one()
            for from_val, to_val in date_ranges:
                competing_google_trends_pull_steps = (
                    session.query(GoogleTrendsPullStep)
                    .join(GoogleTrendsPull)
                    .join(GoogleTrendsGroup)
                    .filter(
                        GoogleTrendsPullStep.timeframe_id == timeframe.id,
                        GoogleTrendsPullStep.from_date == from_val,
                        GoogleTrendsPullStep.to_date == to_val,
                        GoogleTrendsPullStep.is_current.is_(True),
                        GoogleTrendsGroup.google_trends_geo_id == geo.id,
                        GoogleTrendsGroup.google_trends_gprop_id == gprop.id,
                        GoogleTrendsGroup.google_trends_keywords_id == google_trends_keywords.id,
                    )
                    .all()
                )
                valid_competing_found = False
                for competing_google_trends_pull_step in competing_google_trends_pull_steps:
                    for datum in competing_google_trends_pull_step.google_trends_data:
                        if datum.is_partial:
                            competing_google_trends_pull_step.is_current = False
                            break
                    else:
                        if valid_competing_found:
                            competing_google_trends_pull_step.is_current = False
                        valid_competing_found = True
                if valid_competing_found:
                    continue
                google_trends_pull_step = GoogleTrendsPullStep(
                    google_trends_pull_id=google_trends_pull.id,
                    timeframe_id=timeframe.id,
                    from_date=from_val,
                    to_date=to_val,
                )
                session.add(google_trends_pull_step)
                session.flush()
                from_string, to_string = date_range_to_timeframe_string(from_val, to_val)
                timeframe_string = from_string if to_string is None else f"{from_string} {to_string}"
                data = retrieve_interest_over_time_from_google_trends(keywords, geo, gprop, timeframe_string)
                if timeframe_base_label[-1] == "m":
                    data = data[:-1]
                for record in data:
                    data_date = record.pop("data_date")
                    is_partial = bool(record.pop("isPartial"))
                    for keyword, value in record.items():
                        keyword_index = keywords.index(keyword)
                        google_trends = GoogleTrends(
                            google_trends_pull_step_id=google_trends_pull_step.id,
                            google_trends_keyword_index=keyword_index + 1,
                            data_date=data_date,
                            value=value,
                            is_partial=is_partial,
                        )
                        session.add(google_trends)
    session.commit()
