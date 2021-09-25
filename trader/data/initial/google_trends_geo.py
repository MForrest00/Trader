from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from trader.data.initial.base import BaseData
from trader.models.google_trends import GoogleTrendsGeo


@dataclass(frozen=True, eq=True)
class GoogleTrendsGeoData(BaseData):
    code: str
    name: str

    def query_instance(self, session: Session) -> Optional[GoogleTrendsGeo]:
        return session.query(GoogleTrendsGeo).filter_by(code=self.code).one_or_none()

    def create_instance(self) -> GoogleTrendsGeo:
        return GoogleTrendsGeo(code=self.code, name=self.name)


GOOGLE_TRENDS_GEO_WORLDWIDE = GoogleTrendsGeoData("google_trends_geo_worldwide_id", "", "Worldwide")
GOOGLE_TRENDS_GEO_UNITED_STATES = GoogleTrendsGeoData("google_trends_geo_united_states_id", "US", "United States")
GOOGLE_TRENDS_GEOS = (GOOGLE_TRENDS_GEO_WORLDWIDE, GOOGLE_TRENDS_GEO_UNITED_STATES)
