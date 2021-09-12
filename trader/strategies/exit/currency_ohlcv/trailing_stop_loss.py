import pandas as pd
from sqlalchemy.orm.attributes import flag_modified
from trader.models.currency_ohlcv_position import CurrencyOHLCVPosition
from trader.strategies.exit.base import ExitStrategy


class TrailingStopLossCurrencyOHLCVExitStrategy(ExitStrategy):
    NAME = "Trailing Stop Loss"
    VERSION = "1.0.0"
    IS_ENTRY = False
    NORMAL_PARAMETER_SPACE = {"trailing_stop_loss_percentage": [i * 0.01 for i in range(2, 42, 2)]}

    def __init__(self, trailing_stop_loss_percentage: float = 0.15):
        self.trailing_stop_loss_percentage = trailing_stop_loss_percentage

    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe

    def should_close_position(self, position: CurrencyOHLCVPosition, dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if "encountered_max" not in position.data:
            position.data["encountered_max"] = max(position.bought_price, row["close"])
        else:
            position.data["encountered_max"] = max(position.data["encountered_max"], row["close"])
        flag_modified(position, "data")
        if row["close"] <= (position.data["encountered_max"] * (1 - self.trailing_stop_loss_percentage)):
            return True
        return False