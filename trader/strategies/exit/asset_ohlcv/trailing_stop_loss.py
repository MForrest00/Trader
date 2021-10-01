from typing import Dict
import pandas as pd
from sqlalchemy.orm.attributes import flag_modified
from trader.models.position import Position
from trader.strategies.asset_ohlcv.base import AssetOHLCVStrategy
from trader.strategies.exit.base import ExitStrategy


class TrailingStopLossAssetOHLCVExitStrategy(AssetOHLCVStrategy, ExitStrategy):
    NAME = "Trailing Stop Loss"
    VERSION = "1.0.0"
    SUPPLEMENTAL_DATA_FEEDS = ()
    PARAMETER_SPACE = {"trailing_stop_loss_percentage": [i * 0.01 for i in range(2, 42, 2)]}

    def __init__(self, arguments: Dict[str, float]):
        super().__init__(arguments)
        self.trailing_stop_loss_percentage = self.arguments.get("trailing_stop_loss_percentage", 0.15)

    def enhance_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe

    def should_close_position(self, position: Position, dataframe: pd.DataFrame, row_index: int) -> bool:
        row = dataframe.iloc[row_index]
        if "trailing_stop_loss_encountered_max" not in position.data:
            position.data["trailing_stop_loss_encountered_max"] = max(position.bought_price, row["high"])
        else:
            position.data["trailing_stop_loss_encountered_max"] = max(
                position.data["trailing_stop_loss_encountered_max"], row["high"]
            )
        flag_modified(position, "data")
        if row["close"] <= (
            position.data["trailing_stop_loss_encountered_max"] * (1 - self.trailing_stop_loss_percentage)
        ):
            return True
        return False
