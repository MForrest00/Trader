import json
from bs4 import BeautifulSoup
import requests
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, CRYPTOCURRENCY_EXCHANGE
from trader.models.cryptocurrency_exchange import CryptocurrencyExchange
from trader.models.source import Source


def update_cryptocurrency_exchange_ranks_from_coin_market_cap() -> None:
    response = requests.get("https://coinmarketcap.com/rankings/exchanges/")
    soup = BeautifulSoup(response.text, "lxml")
    data = json.loads(soup.select("script#__NEXT_DATA__")[0].string)
    coin_market_cap_id = int(cache.get(COIN_MARKET_CAP.cache_key).decode())
    cryptocurrency_exchange_id = int(cache.get(CRYPTOCURRENCY_EXCHANGE.cache_key).decode())
    with DBSession() as session:
        for cryptocurrency_exchange_rank in data["props"]["initialProps"]["pageProps"]["exchange"]:
            cryptocurrency_exchange = (
                session.query(CryptocurrencyExchange)
                .join(Source)
                .filter(
                    Source.name == cryptocurrency_exchange_rank["name"],
                    Source.source_type_id == cryptocurrency_exchange_id,
                )
                .first()
            )
