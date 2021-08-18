import json
from bs4 import BeautifulSoup
import requests


def update_cryptocurrency_exchange_ranks_from_coin_market_cap() -> None:
    response = requests.get("https://coinmarketcap.com/rankings/exchanges/")
    soup = BeautifulSoup(response.text, "lxml")
    data = json.loads(soup.select("script#__NEXT_DATA__")[0].string)
    for cryptocurrency_exchange in data["props"]["initialProps"]["pageProps"]["exchange"]:
        pass
