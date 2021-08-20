import json
from bs4 import BeautifulSoup
import requests
from trader.connections.cache import cache
from trader.connections.database import DBSession
from trader.data.base import COIN_MARKET_CAP, CRYPTOCURRENCY_EXCHANGE
from trader.models.country import Country
from trader.models.cryptocurrency_exchange import (
    CryptocurrencyExchange,
    CryptocurrencyExchangeCountry,
    CryptocurrencyExchangeStandardCurrency,
)
from trader.models.cryptocurrency_exchange_rank import CryptocurrencyExchangeRank, CryptocurrencyExchangeRankPull
from trader.models.currency import Currency
from trader.models.standard_currency import StandardCurrency
from trader.models.source import Source
from trader.utilities.functions import iso_time_string_to_datetime


def update_cryptocurrency_exchange_ranks_from_coin_market_cap() -> None:
    coin_market_cap_id = int(cache.get(COIN_MARKET_CAP.cache_key).decode())
    cryptocurrency_exchange_id = int(cache.get(CRYPTOCURRENCY_EXCHANGE.cache_key).decode())
    response = requests.get("https://coinmarketcap.com/rankings/exchanges/")
    soup = BeautifulSoup(response.text, "lxml")
    data = json.loads(soup.select("script#__NEXT_DATA__")[0].string)
    cryptocurrency_exchange_ranks = data["props"]["initialProps"]["pageProps"]["exchange"]
    if cryptocurrency_exchange_ranks:
        with DBSession() as session:
            cryptocurrency_exchange_rank_pull = CryptocurrencyExchangeRankPull(source_id=coin_market_cap_id)
            session.add(cryptocurrency_exchange_rank_pull)
            session.flush()
            for record in cryptocurrency_exchange_ranks:
                name = record["name"]
                source_entity_id = record["id"]
                source_slug = record["slug"]
                source_date_launched = (
                    iso_time_string_to_datetime(record["dateLaunched"]) if record["dateLaunched"] else None
                )
                source_date_last_updated = iso_time_string_to_datetime(record["lastUpdated"])
                standard_currency_symbols = record["fiats"]
                country_iso_alpha_2_codes = record["countries"]
                source = (
                    session.query(Source).filter_by(name=name, source_type_id=cryptocurrency_exchange_id).one_or_none()
                )
                if not source:
                    source = Source(source_id=coin_market_cap_id, name=name, source_type_id=cryptocurrency_exchange_id)
                    session.add(source)
                    session.flush()
                cryptocurrency_exchange = source.cryptocurrency_exchange
                if not cryptocurrency_exchange:
                    cryptocurrency_exchange = CryptocurrencyExchange(
                        source_id=source.id,
                        source_entity_id=source_entity_id,
                        source_slug=source_slug,
                        source_date_launched=source_date_launched,
                        source_date_last_updated=source_date_last_updated,
                    )
                    session.add(cryptocurrency_exchange)
                    session.flush()
                elif cryptocurrency_exchange.source_date_last_updated < source_date_last_updated:
                    cryptocurrency_exchange.update(
                        {
                            "source_entity_id": source_entity_id,
                            "source_slug": source_slug,
                            "source_date_launched": source_date_launched,
                            "source_date_last_updated": source_date_last_updated,
                        }
                    )
                    for item in cryptocurrency_exchange.standard_currencies:
                        if item.standard_currency.currency.symbol not in standard_currency_symbols:
                            session.delete(item)
                    for item in cryptocurrency_exchange.countries:
                        if item.country.iso_alpha_2_code not in country_iso_alpha_2_codes:
                            session.delete(item)
                for standard_currency_symbol in standard_currency_symbols:
                    standard_currency = (
                        session.query(StandardCurrency)
                        .join(Currency)
                        .filter(Currency.symbol == standard_currency_symbol)
                        .one_or_none()
                    )
                    if standard_currency:
                        cryptocurrency_exchange_standard_currency = (
                            session.query(CryptocurrencyExchangeStandardCurrency)
                            .filter_by(
                                cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                                standard_currency_id=standard_currency.id,
                            )
                            .one_or_none()
                        )
                        if not cryptocurrency_exchange_standard_currency:
                            cryptocurrency_exchange_standard_currency = CryptocurrencyExchangeStandardCurrency(
                                source_id=coin_market_cap_id,
                                cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                                standard_currency_id=standard_currency.id,
                            )
                            session.add(cryptocurrency_exchange_standard_currency)
                for country_iso_alpha_2_code in country_iso_alpha_2_codes:
                    country = session.query(Country).filter_by(iso_alpha_2_code=country_iso_alpha_2_code).one_or_none()
                    if country:
                        cryptocurrency_exchange_country = (
                            session.query(CryptocurrencyExchangeCountry)
                            .filter_by(
                                cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                                country_id=country.id,
                            )
                            .one_or_none()
                        )
                        if not cryptocurrency_exchange_country:
                            cryptocurrency_exchange_country = CryptocurrencyExchangeCountry(
                                source_id=coin_market_cap_id,
                                cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                                country_id=country.id,
                            )
                            session.add(cryptocurrency_exchange_country)
                cryptocurrency_exchange_rank = CryptocurrencyExchangeRank(
                    cryptocurrency_exchange_rank_pull_id=cryptocurrency_exchange_rank_pull.id,
                    cryptocurrency_exchange_id=cryptocurrency_exchange.id,
                    rank=record["rank"],
                    spot_vol_24h=record.get("spotVol24h"),
                    derivatives_vol_24h=record.get("derivativesVol24h"),
                    derivatives_open_interests=record.get("derivativesOpenInterests"),
                    weekly_web_visits=record["visits"],
                    market_share_percentage=record.get("marketSharePct"),
                    maker_fee=record["makerFee"],
                    taker_fee=record["takerFee"],
                    source_score=record["score"],
                    source_liquidity_score=record["liquidity"],
                )
                session.add(cryptocurrency_exchange_rank)
            session.commit()
