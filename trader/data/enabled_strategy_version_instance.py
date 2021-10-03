from trader.connections.database import session
from trader.models.enabled_strategy_version_instance import EnabledStrategyVersionInstance
from trader.models.strategy import Strategy, StrategyVersion, StrategyVersionInstance
from trader.utilities.initial_enabled_data import (
    INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES,
    INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES,
)


def set_initial_enabled_strategy_version_instances() -> None:
    timeframes = (
        INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES.keys() | INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES.keys()
    )
    for timeframe in timeframes:
        timeframe_id = timeframe.fetch_id()
        enabled_strategy_version_instances = (
            *INITIAL_ENTRY_ENABLED_STRATEGY_VERSION_INSTANCES.get(timeframe, ()),
            *INITIAL_EXIT_ENABLED_STRATEGY_VERSION_INSTANCES.get(timeframe, ()),
        )
        for enabled_strategy_version_instance in enabled_strategy_version_instances:
            strategy_version_instance = (
                session.query(StrategyVersionInstance)
                .join(StrategyVersion)
                .join(Strategy)
                .filter(
                    Strategy.name == enabled_strategy_version_instance.strategy.NAME,
                    Strategy.is_entry.is_(enabled_strategy_version_instance.strategy.IS_ENTRY),
                    StrategyVersion.version == enabled_strategy_version_instance.strategy.VERSION,
                    StrategyVersionInstance.arguments == enabled_strategy_version_instance.arguments,
                )
                .one_or_none()
            )
            if strategy_version_instance:
                enabled_strategy_version_instance = EnabledStrategyVersionInstance(
                    strategy_version_instance_id=strategy_version_instance.id,
                    timeframe_id=timeframe_id,
                    priority=enabled_strategy_version_instance.priority,
                )
                session.add(enabled_strategy_version_instance)
            else:
                strategy_version = enabled_strategy_version_instance.strategy.get_strategy_version()
                strategy_version_instance = StrategyVersionInstance(
                    strategy_version_id=strategy_version.id,
                    arguments=enabled_strategy_version_instance.arguments,
                )
                session.add(strategy_version_instance)
                session.flush()
                enabled_strategy_version_instance = EnabledStrategyVersionInstance(
                    strategy_version_instance_id=strategy_version_instance.id,
                    timeframe_id=timeframe_id,
                    priority=enabled_strategy_version_instance.priority,
                )
                session.add(enabled_strategy_version_instance)
    session.commit()
