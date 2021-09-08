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

    @abstractmethod
    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        ...
