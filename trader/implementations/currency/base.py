from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple
import pandas as pd
from trader.models.currency import Currency
from trader.models.currency_ohlcv_position import CurrencyOHLCVPosition
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.strategies.currency.base import CurrencyStrategy


class CurrencyImplementation(ABC):
    def __init__(
        self,
        source: Source,
        base_currency: Currency,
        quote_currency: Currency,
        timeframe: Timeframe,
        from_inclusive: Optional[datetime],
        dataframe_minimum_date: datetime,
        dataframe_start_date: datetime,
        available_quote_currency: float,
        target_position_size: float,
        entrance_strategy_parameters: Sequence[Dict[str, Any]],
        exit_strategy_parameters: Sequence[Dict[str, Any]],
    ):
        self.source = source
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.timeframe = timeframe
        self.from_inclusive = from_inclusive
        self.dataframe_minimum_date = dataframe_minimum_date
        self.dataframe_start_date = dataframe_start_date
        self.available_quote_currency = available_quote_currency
        self.target_position_size = target_position_size
        self.entrance_strategies = [s(**p) for s, p in zip(self.ENTRANCE_STRATEGIES, entrance_strategy_parameters)]
        self.exit_strategies = [s(**p) for s, p in zip(self.EXIT_STRATEGIES, exit_strategy_parameters)]
        self.implementation_version_id = self.fetch_implementation_version_id()
        self.open_positions = self.fetch_open_positions()
        self.closed_positions = self.fetch_closed_positions()
        self.entrance_strategy_version_id_lookup = self.generate_strategy_version_id_lookup(True)
        self.exit_strategy_version_id_lookup = self.generate_strategy_version_id_lookup(False)
        self.dataframe = self.refine_dataframe(self.generate_dataframe())

    @property
    @abstractmethod
    def NAME(self) -> str:
        ...

    @property
    @abstractmethod
    def VERSION(self) -> str:
        ...

    @property
    @abstractmethod
    def ENTRANCE_STRATEGIES(self) -> Tuple[CurrencyStrategy]:
        ...

    @property
    @abstractmethod
    def EXIT_STRATEGIES(self) -> Tuple[CurrencyStrategy]:
        ...

    @abstractmethod
    def fetch_implementation_version_id(self) -> int:
        ...

    @abstractmethod
    def fetch_open_positions(self) -> List[CurrencyOHLCVPosition]:
        ...

    @abstractmethod
    def fetch_closed_positions(self) -> List[CurrencyOHLCVPosition]:
        ...

    @staticmethod
    @abstractmethod
    def fetch_strategy_version_id(strategy: CurrencyStrategy, is_entrance: bool) -> int:
        ...

    @classmethod
    def generate_strategy_version_id_lookup(cls, is_entrance: bool) -> Dict[str, int]:
        output: Dict[str, int] = {}
        strategies = cls.ENTRANCE_STRATEGIES if is_entrance else cls.EXIT_STRATEGIES
        for strategy in strategies:
            output[strategy.NAME] = cls.fetch_strategy_version_id(strategy, is_entrance)
        return output

    @classmethod
    def refine_dataframe(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        for entrance_strategy in cls.ENTRANCE_STRATEGIES:
            dataframe = entrance_strategy.refine_dataframe(dataframe)
        for exit_strategy in cls.EXIT_STRATEGIES:
            dataframe = exit_strategy.refine_dataframe(dataframe)
        return dataframe

    @abstractmethod
    def generate_dataframe(self) -> pd.DataFrame:
        ...

    def generate_df_range(self) -> range:
        range_end = self.dataframe.shape[0]
        if self.dataframe_start_date:
            try:
                return range(self.dataframe.index.get_loc(self.dataframe_start_date), range_end)
            except KeyError:
                pass
        if self.dataframe_minimum_date:
            try:
                return range(self.dataframe.index.get_loc(self.dataframe_minimum_date), range_end)
            except KeyError:
                pass
        return range(0, range_end)

    @abstractmethod
    def can_open_position(self) -> bool:
        ...

    def strategy_is_alive(self) -> bool:
        return self.open_positions or self.can_open_position()

    def run_implementation(self) -> None:
        for i in self.generate_df_range():
            if not self.strategy_is_alive():
                break
            closed_positions_indexes: List[int] = []
            for position in self.open_positions:
                for j, strategy in enumerate(self.exit_strategies):
                    if strategy.should_close_position(position, self.dataframe, i):
                        closed_positions_indexes.append(j)
                        break
            if closed_positions_indexes:
                self.closed_positions.extend(p for j, p in self.open_positions if j in closed_positions_indexes)
                self.open_positions = [p for j, p in self.open_positions if j not in closed_positions_indexes]
            if self.can_open_position():
                for strategy in self.entrance_strategies:
                    if strategy.should_open_position(self.dataframe, i):
                        pass
