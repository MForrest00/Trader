from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Optional
import pandas as pd
from trader.models.currency_ohlcv_position import CurrencyOHLCVPosition


class Implementation(ABC):
    def __init__(
        self,
        base_ohlcv_df: pd.DataFrame,
        available_quote_currency: float,
        position_value: float,
        take_profits_percentage: float,
        min_open_date: Optional[datetime] = None,
        start_index: Optional[int] = 0,
    ):
        self.base_ohlcv_df = base_ohlcv_df
        self.ohlcv_df = self.generate_ohlcv_df()
        self.available_quote_currency = available_quote_currency
        self.position_value = position_value
        self.take_profits_percentage = take_profits_percentage
        self.min_open_date = min_open_date
        self.start_index = start_index
        self.open_positions: List[Position] = []
        self.closed_positions: List[Position] = []

    @abstractmethod
    def generate_ohlcv_df(self) -> pd.DataFrame:
        ...

    def generate_df_range(self) -> range:
        if self.min_open_date:
            try:
                min_open_date_start_index = self.ohlcv_df.index.get_loc(self.min_open_date)
            except KeyError:
                min_open_date_start_index = 0
        start_index = max(min_open_date_start_index, self.start_index)
        return range(start_index, self.ohlcv_df.shape[0])

    def can_open_position(self) -> bool:
        return self.position_value <= self.available_quote_currency

    def strategy_is_alive(self) -> bool:
        return self.open_positions or self.can_open_position()

    @abstractmethod
    def should_open_position(self, df_index: int) -> bool:
        ...

    def open_position(self, id: int, purchased_price: float) -> None:
        self.open_positions.append(
            Position(open_record_id=id, size=self.position_value / purchased_price, purchased_price=purchased_price)
        )

    @abstractmethod
    def should_close_position(self, position: Position, df_index: int) -> bool:
        ...

    def close_position(self, position: Position, df_index: int) -> None:
        position.closed_record_id = id
        position.sold_price = self.ohlcv_df.iloc[df_index]["close"]
        returns = (position.size * position.sold_price) - (position.size * position.purchased_price)
        if returns > 0:
            returns -= returns * self.take_profits_percentage
        self.available_quote_currency += returns

    def run_strategy(self):
        for i in self.generate_df_range():
            if not self.strategy_is_alive():
                break
            if self.should_open_position(i):
                self.open_position(i)
            closed_position_indices: Set[int] = set()
            for j, position in enumerate(self.open_positions):
                if self.should_close_position(position, i):
                    self.close_position(position, i)
                    closed_position_indices.add(j)
            self.closed_positions.extend([p for j, p in enumerate(self.open_positions) if j in closed_position_indices])
            self.open_positions = [p for j, p in enumerate(self.open_positions) if j not in closed_position_indices]
