from abc import ABC, abstractmethod
import pandas as pd


class CurrencyStrategy(ABC):
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
    def IS_ENTRANCE(self) -> bool:
        ...

    @abstractmethod
    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        ...
