from datetime import date, datetime, timezone
from typing import Dict, List, Optional, Tuple, Union
from pytrends.request import TrendReq
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.persistence.models.google_trends import GoogleTrendsPullGeo, GoogleTrendsPullKeyword
from trader.persistence.models.timeframe import Timeframe
from trader.utilities.functions import clean_range_cap, google_trends_date_ranges_to_timeframe


def retrieve_interest_over_time(
    keywords: GoogleTrendsPullKeyword,
    geo: GoogleTrendsPullGeo,
    from_inclusive: Union[date, datetime],
    to_exclusive: Optional[Union[date, datetime]] = None,
) -> Tuple[Timeframe, List[Dict[str, Union[datetime, int, bool]]]]:
    timeframe_data = google_trends_date_ranges_to_timeframe(from_inclusive, to_exclusive)
    with DBSession() as session:
        timeframe = session.query(Timeframe).get(int(cache.get(timeframe_data.cache_key).decode()))
    if to_exclusive:
        timeframe_unit = timeframe.base_label[-1:]
        from_inclusive = clean_range_cap(from_inclusive, timeframe_unit)
        to_exclusive = (
            clean_range_cap(min(to_exclusive, datetime.utcnow()), timeframe_unit)
            if to_exclusive
            else clean_range_cap(datetime.utcnow(), timeframe_unit)
        )
        if not from_inclusive < to_exclusive:
            raise ValueError("From argument must be less than the to argument")
        if timeframe_unit == "m":
            timeframe_string = f"{from_inclusive.strftime('%Y-%m-%d')}T00 {to_exclusive.strftime('%Y-%m-%d')}T00"
        else:
            timeframe_string = f"{from_inclusive.strftime('%Y-%m-%d')} {to_exclusive.strftime('%Y-%m-%d')}"
    else:
        timeframe_string = "all"
    pytrends = TrendReq()
    pytrends.build_payload(keywords.keywords, timeframe=timeframe_string, geo=geo)
    data = pytrends.interest_over_time().to_dict("index")
    output: List[Dict[str, Union[datetime, int, bool]]] = []
    for time, columns in data.items():
        item_data = {"time": time.to_pydatetime().replace(tzinfo=timezone.utc)}
        item_data.update(columns)
        output.append(item_data)
    return timeframe, sorted(output, key=lambda x: x["time"])
