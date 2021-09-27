from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from trader.data.initial.data_feed import DataFeedData
from trader.models.strategy import Strategy as StrategyModel, StrategyVersion, StrategyVersionInstance


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

    def __init__(self, arguments: Dict[str, Any]):
        self.arguments = arguments

    def get_strategy_version_instance(self, session: Session) -> StrategyVersionInstance:
        return (
            session.query(StrategyVersionInstance)
            .join(StrategyVersion)
            .join(StrategyModel)
            .filter(
                StrategyModel.name == self.NAME,
                StrategyModel.is_entry == self.IS_ENTRY,
                StrategyVersion.version == self.VERSION,
                StrategyVersionInstance.arguments == self.arguments,
            )
            .one()
        )

    @abstractmethod
    def enhance_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        ...
