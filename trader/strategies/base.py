from abc import ABC, abstractmethod
from typing import Any, Dict, Sequence, Tuple
import pandas as pd
from trader.connections.database import session
from trader.data.initial.data_feed import DataFeedData
from trader.models.strategy import Strategy as StrategyModel, StrategyVersion, StrategyVersionInstance


class Strategy(ABC):
    @property
    @abstractmethod
    def NAME(self) -> str:
        ...

    @property
    @abstractmethod
    def IS_ENTRY(self) -> bool:
        ...

    @property
    @abstractmethod
    def VERSION(self) -> str:
        ...

    @property
    @abstractmethod
    def DATA_FEEDS(self) -> Tuple[DataFeedData]:
        ...

    @property
    @abstractmethod
    def PARAMETER_SPACE(self) -> Dict[str, Sequence[Any]]:
        ...

    def __init__(self, arguments: Dict[str, Any]):
        self.arguments = arguments

    @classmethod
    def get_cache_key(cls) -> str:
        strategy_type = "entry" if cls.IS_ENTRY else "exit"
        strategy_name = "_".join(cls.NAME.lower().split())
        return f"strategy_version_{strategy_type}_{strategy_name}_id"

    def get_strategy_version_instance(self) -> StrategyVersionInstance:
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
