from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from trader.connections.database import session
from trader.data.initial.source import SourceData
from trader.data.initial.source_type import SourceTypeData
from trader.models.asset import Asset
from trader.models.asset_ohlcv import AssetOHLCV, AssetOHLCVGroup, AssetOHLCVPull
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.utilities.functions import clean_range_cap


class AssetOHLCVDataFeedRetriever(ABC):
    def __init__(
        self,
        base_asset: Asset,
        quote_asset: Asset,
        timeframe: Timeframe,
        from_inclusive: datetime,
        to_exclusive: Optional[datetime] = None,
    ):
        self.base_asset = base_asset
        self.quote_asset = quote_asset
        self.timeframe = timeframe
        self.from_inclusive = clean_range_cap(from_inclusive, timeframe.unit)
        self.to_exclusive = clean_range_cap(self.get_to_exclusive(to_exclusive), timeframe.unit)
        self._source_id = None
        self.validate_attributes()

    @property
    @abstractmethod
    def SOURCE(self) -> Union[SourceData, Tuple[str, SourceTypeData]]:
        ...

    @property
    def source_id(self) -> int:
        if self._source_id is None:
            if isinstance(self.SOURCE, tuple):
                name, source_type_data = self.SOURCE
                source = session.query(Source).filter_by(source_type_id=source_type_data.fetch_id(), name=name).one()
                self._source_id = source.id
            else:
                self._source_id = self.SOURCE.fetch_id()
        return self._source_id

    @abstractmethod
    def get_to_exclusive(self, to_exclusive: Optional[datetime]) -> datetime:
        ...

    @abstractmethod
    def validate_attributes(self) -> bool:
        ...

    @abstractmethod
    def retrieve_asset_ohlcv(self) -> List[Dict[str, Optional[Union[datetime, int, float]]]]:
        ...

    def update_asset_ohlcv(self) -> int:
        data = self.retrieve_asset_ohlcv()
        asset_ohlcv_group = (
            session.query(AssetOHLCVGroup)
            .filter_by(
                source_id=self.source_id,
                base_asset_id=self.base_asset.id,
                quote_asset_id=self.quote_asset.id,
                timeframe_id=self.timeframe.id,
            )
            .one_or_none()
        )
        if not asset_ohlcv_group:
            asset_ohlcv_group = AssetOHLCVGroup(
                source_id=self.source_id,
                base_asset_id=self.base_asset.id,
                quote_asset_id=self.quote_asset.id,
                timeframe_id=self.timeframe.id,
            )
            session.add(asset_ohlcv_group)
            session.flush()
        asset_ohlcv_pull = AssetOHLCVPull(
            asset_ohlcv_group_id=asset_ohlcv_group.id,
            from_inclusive=self.from_inclusive,
            to_exclusive=self.to_exclusive,
        )
        session.add(asset_ohlcv_pull)
        session.flush()
        new_records_inserted = 0
        if data:
            existing_records = (
                session.query(AssetOHLCV)
                .join(AssetOHLCVPull)
                .join(AssetOHLCVGroup)
                .filter(
                    AssetOHLCVGroup.source_id == self.source_id,
                    AssetOHLCVGroup.base_asset_id == self.base_asset.id,
                    AssetOHLCVGroup.quote_asset_id == self.quote_asset.id,
                    AssetOHLCVGroup.timeframe_id == self.timeframe.id,
                    AssetOHLCV.date_open >= data[0]["date_open"],
                    AssetOHLCV.date_open <= data[-1]["date_open"],
                )
                .all()
            )
            existing_date_opens = set(r.date_open for r in existing_records)
            for record in data:
                if record["date_open"] not in existing_date_opens:
                    asset_ohlcv = AssetOHLCV(asset_ohlcv_pull_id=asset_ohlcv_pull.id, **record)
                    session.add(asset_ohlcv)
                    new_records_inserted += 1
        session.commit()
        return new_records_inserted
