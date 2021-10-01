from abc import abstractmethod
import pandas as pd
from trader.models.position import Position
from trader.strategies.base import Strategy


class ExitStrategy(Strategy):
    IS_ENTRY = False

    @abstractmethod
    def should_close_position(self, position: Position, dataframe: pd.DataFrame, row_index: int) -> bool:
        ...
