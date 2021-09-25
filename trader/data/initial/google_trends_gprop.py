from dataclasses import dataclass
from typing import Optional
from sqlalchemy.orm import Session
from trader.data.initial.base import BaseData
from trader.models.google_trends import GoogleTrendsGprop


@dataclass(frozen=True, eq=True)
class GoogleTrendsGpropData(BaseData):
    code: str
    name: str

    def query_instance(self, session: Session) -> Optional[GoogleTrendsGprop]:
        return session.query(GoogleTrendsGprop).filter_by(code=self.code).one_or_none()

    def create_instance(self) -> GoogleTrendsGprop:
        return GoogleTrendsGprop(code=self.code, name=self.name)


GOOGLE_TRENDS_GPROP_WEB_SEARCH = GoogleTrendsGpropData("google_trends_gprop_web_search_id", "", "Web search")
GOOGLE_TRENDS_GPROP_IMAGE_SEARCH = GoogleTrendsGpropData("google_trends_gprop_image_search_id", "image", "Image search")
GOOGLE_TRENDS_GPROP_NEWS_SEARCH = GoogleTrendsGpropData("google_trends_gprop_news_search_id", "news", "News search")
GOOGLE_TRENDS_GPROP_GOOGLE_SHOPPING = GoogleTrendsGpropData(
    "google_trends_gprop_google_shopping_id", "froogle", "Google shopping"
)
GOOGLE_TRENDS_GPROP_YOUTUBE_SEARCH = GoogleTrendsGpropData(
    "google_trends_gprop_youtube_search_id", "youtube", "YouTube search"
)
GOOGLE_TRENDS_GPROPS = (
    GOOGLE_TRENDS_GPROP_WEB_SEARCH,
    GOOGLE_TRENDS_GPROP_IMAGE_SEARCH,
    GOOGLE_TRENDS_GPROP_NEWS_SEARCH,
    GOOGLE_TRENDS_GPROP_GOOGLE_SHOPPING,
    GOOGLE_TRENDS_GPROP_YOUTUBE_SEARCH,
)
