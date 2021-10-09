from abc import abstractmethod
from typing import Any, Dict
import pandas as pd
from sqlalchemy.orm.attributes import flag_modified
from trader.models.asset import Asset
from trader.models.position import Position
from trader.strategies.base import Strategy


class ExitStrategy(Strategy):
    IS_ENTRY = False

    def __init__(self, base_asset: Asset, arguments: Dict[str, Any], position: Position):
        super().__init__(base_asset, arguments)
        self.position = position

    def flag_position_data_modified(self) -> None:
        flag_modified(self.position, "data")

    @abstractmethod
    def get_sell_signal_strength(self, dataframe: pd.DataFrame, row_index: int) -> float:
        ...
