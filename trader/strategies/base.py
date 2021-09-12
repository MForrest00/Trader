from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence
import pandas as pd


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
    def NORMAL_PARAMETER_SPACE(self) -> Dict[str, Sequence[Any]]:
        ...

    @abstractmethod
    def refine_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        ...
