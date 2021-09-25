from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence, Tuple
import pandas as pd
from trader.data.initial.data_feed import DataFeedData


class Strategy(ABC):
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
    def IS_ENTRY(self) -> bool:
        ...

    @property
    @abstractmethod
    def BASE_DATA_FEED(self) -> DataFeedData:
        ...

    @property
    @abstractmethod
    def SUPPLEMENTAL_DATA_FEEDS(self) -> Tuple[DataFeedData]:
        ...

    @property
    @abstractmethod
    def PARAMETER_SPACE(self) -> Dict[str, Sequence[Any]]:
        ...

    @abstractmethod
    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        ...
