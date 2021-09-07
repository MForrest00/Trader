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

    @staticmethod
    @abstractmethod
    def refine_dataframe(dataframe: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        ...
