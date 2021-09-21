from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from trader.connections.database import DBSession
from trader.data.base import SourceData, SourceTypeData
from trader.models.currency import Currency
from trader.models.currency_ohlcv import CurrencyOHLCV, CurrencyOHLCVGroup, CurrencyOHLCVPull
from trader.models.source import Source
from trader.models.timeframe import Timeframe
from trader.utilities.functions import clean_range_cap, fetch_base_data_id


class CurrencyOHLCVDataFeedRetriever(ABC):
    def __init__(
        self,
        base_currency: Currency,
        quote_currency: Currency,
        timeframe: Timeframe,
        from_inclusive: datetime,
        to_exclusive: Optional[datetime] = None,
    ):
        self.base_currency = base_currency
        self.quote_currency = quote_currency
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
                with DBSession() as session:
                    source = (
                        session.query(Source)
                        .filter_by(source_type_id=fetch_base_data_id(source_type_data), name=name)
                        .one()
                    )
                self._source_id = source.id
            else:
                self._source_id = fetch_base_data_id(self.SOURCE)
        return self._source_id

    @abstractmethod
    def get_to_exclusive(self, to_exclusive: Optional[datetime]) -> datetime:
        ...

    @abstractmethod
    def validate_attributes(self) -> bool:
        ...

    @abstractmethod
    def retrieve_currency_ohlcv(self, *args, **kwargs) -> List[Dict[str, Optional[Union[datetime, int, float]]]]:
        ...

    def update_currency_ohlcv(self) -> int:
        data = self.retrieve_currency_ohlcv()
        with DBSession() as session:
            currency_ohlcv_group = (
                session.query(CurrencyOHLCVGroup)
                .filter_by(
                    source_id=self.source_id,
                    base_currency_id=self.base_currency.id,
                    quote_currency_id=self.quote_currency.id,
                    timeframe_id=self.timeframe.id,
                )
                .one_or_none()
            )
            if not currency_ohlcv_group:
                currency_ohlcv_group = CurrencyOHLCVGroup(
                    source_id=self.source_id,
                    base_currency_id=self.base_currency.id,
                    quote_currency_id=self.quote_currency.id,
                    timeframe_id=self.timeframe.id,
                )
                session.add(currency_ohlcv_group)
                session.flush()
            currency_ohlcv_pull = CurrencyOHLCVPull(
                currency_ohlcv_group_id=currency_ohlcv_group.id,
                from_inclusive=self.from_inclusive,
                to_exclusive=self.to_exclusive,
            )
            session.add(currency_ohlcv_pull)
            session.flush()
            new_records_inserted = 0
            if data:
                existing_records = (
                    session.query(CurrencyOHLCV)
                    .join(CurrencyOHLCVPull)
                    .join(CurrencyOHLCVGroup)
                    .filter(
                        CurrencyOHLCVGroup.source_id == self.source_id,
                        CurrencyOHLCVGroup.base_currency_id == self.base_currency.id,
                        CurrencyOHLCVGroup.quote_currency_id == self.quote_currency.id,
                        CurrencyOHLCVGroup.timeframe_id == self.timeframe.id,
                        CurrencyOHLCV.date_open >= data[0]["date_open"],
                        CurrencyOHLCV.date_open <= data[-1]["date_open"],
                    )
                    .all()
                )
                existing_date_opens = set(r.date_open for r in existing_records)
                for record in data:
                    if record["date_open"] not in existing_date_opens:
                        currency_ohlcv = CurrencyOHLCV(currency_ohlcv_pull_id=currency_ohlcv_pull.id, **record)
                        session.add(currency_ohlcv)
                        new_records_inserted += 1
            session.commit()
        return new_records_inserted
