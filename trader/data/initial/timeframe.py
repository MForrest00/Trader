from dataclasses import dataclass
from typing import Optional
from trader.connections.database import session
from trader.data.initial.base import BaseData
from trader.models.timeframe import Timeframe


@dataclass(frozen=True, eq=True)
class TimeframeData(BaseData):
    base_label: str
    seconds_length: Optional[int]
    unit: str
    amount: int
    ccxt_label: str

    def query_instance(self) -> Optional[Timeframe]:
        return session.query(Timeframe).filter_by(base_label=self.base_label).one_or_none()

    def create_instance(self) -> Timeframe:
        return Timeframe(
            base_label=self.base_label,
            seconds_length=self.seconds_length,
            unit=self.unit,
            amount=self.amount,
            ccxt_label=self.ccxt_label,
        )


TIMEFRAME_ONE_MINUTE = TimeframeData("timeframe_one_minute_id", "1m", 60, "m", 1, "1m")
TIMEFRAME_FIVE_MINUTE = TimeframeData("timeframe_five_minute_id", "5m", 60 * 5, "m", 5, "5m")
TIMEFRAME_EIGHT_MINUTE = TimeframeData("timeframe_eight_minute_id", "8m", 60 * 8, "m", 8, "8m")
TIMEFRAME_FIFTEEN_MINUTE = TimeframeData("timeframe_fifteen_minute_id", "15m", 60 * 15, "m", 15, "15m")
TIMEFRAME_THIRTY_MINUTE = TimeframeData("timeframe_thirty_minute_id", "30m", 60 * 30, "m", 30, "30m")
TIMEFRAME_ONE_HOUR = TimeframeData("timeframe_one_hour_id", "1h", 60 * 60, "h", 1, "1h")
TIMEFRAME_ONE_DAY = TimeframeData("timeframe_one_day_id", "1d", 60 * 60 * 24, "d", 1, "1d")
TIMEFRAME_ONE_MONTH = TimeframeData("timeframe_one_month_id", "1M", None, "M", 1, "1M")
TIMEFRAMES = (
    TIMEFRAME_ONE_MINUTE,
    TIMEFRAME_FIVE_MINUTE,
    TIMEFRAME_EIGHT_MINUTE,
    TIMEFRAME_FIFTEEN_MINUTE,
    TIMEFRAME_THIRTY_MINUTE,
    TIMEFRAME_ONE_HOUR,
    TIMEFRAME_ONE_DAY,
    TIMEFRAME_ONE_MONTH,
)
