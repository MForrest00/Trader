import pandas as pd
from sqlalchemy.orm.attributes import flag_modified
from trader.models.currency_position import CurrencyPosition
from trader.strategies.currency.exit.base import ExitCurrencyStrategy


class TrailingStopLossCurrencyOHLCVExitCurrencyStrategy(ExitCurrencyStrategy):
    NAME = "Trailing Stop Loss"
    VERSION = "1.0.0"

    @staticmethod
    def refine_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe

    @staticmethod
    def should_close_position(
        position: CurrencyPosition,
        dataframe: pd.DataFrame,
        row_index: int,
        grace_periods: int,
        trailing_stop_loss_percentage: float,
    ) -> bool:
        row = dataframe.iloc[row_index]
        if "encountered_max" not in position.data:
            position.data["encountered_max"] = max(position.bought_price, row["close"])
        else:
            position.data["encountered_max"] = max(position.data["encountered_max"], row["close"])
        flag_modified(position, "data")
        if row_index - position.open_dataframe_row_index <= grace_periods:
            return False
        if row["close"] <= (position.data["encountered_max"] * (1 - trailing_stop_loss_percentage)):
            return True
        return False
