import pandas as pd
from sqlalchemy.orm.attributes import flag_modified
from trader.models.currency_position import CurrencyPosition
from trader.strategies.currency.exit.base import ExitCurrencyStrategy


class TrailingStopLossCurrencyOHLCVExitCurrencyStrategy(ExitCurrencyStrategy):
    NAME = "Trailing Stop Loss"
    VERSION = "1.0.0"

    def __init__(self, grace_periods: int, trailing_stop_loss_percentage: float):
        self.grace_periods = grace_periods
        self.trailing_stop_loss_percentage = trailing_stop_loss_percentage

    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe

    def should_close_position(self, position: CurrencyPosition, dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if "encountered_max" not in position.data:
            position.data["encountered_max"] = max(position.bought_price, row["close"])
        else:
            position.data["encountered_max"] = max(position.data["encountered_max"], row["close"])
        flag_modified(position, "data")
        if row_index - position.open_dataframe_row_index <= self.grace_periods:
            return False
        if row["close"] <= (position.data["encountered_max"] * (1 - self.trailing_stop_loss_percentage)):
            return True
        return False
