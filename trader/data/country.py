from bs4 import BeautifulSoup
import requests
from trader.connections.database import session
from trader.data.initial.source import SOURCE_ISO
from trader.models.country import Country


def update_countries_from_iso() -> None:
    iso_id = SOURCE_ISO.fetch_id()
    response = requests.get("https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes")
    soup = BeautifulSoup(response.text, "lxml")
    table_h2 = soup.select("span#Current_ISO_3166_country_codes")[0]
    table_body_rows = table_h2.parent.next_sibling.next_sibling.next_sibling.next_sibling.find_all("tr")[2:]
    for table_body_row in table_body_rows:
        table_data = table_body_row.find_all("td")
        if len(table_data) == 1:
            continue
        name = table_data[0].find_all(text=True)[1]
        official_name = table_data[1].find_all(text=True)[0]
        iso_alpha_2_code = table_data[3].text.strip("\n")
        iso_alpha_3_code = table_data[4].text.strip("\n")
        iso_numeric_code = table_data[5].text.strip("\n")
        country = session.query(Country).filter_by(iso_alpha_3_code=iso_alpha_3_code).one_or_none()
        if not country:
            country = Country(
                source_id=iso_id,
                name=name,
                official_name=official_name,
                iso_alpha_2_code=iso_alpha_2_code,
                iso_alpha_3_code=iso_alpha_3_code,
                iso_numeric_code=iso_numeric_code,
            )
            session.add(country)
        else:
            country.name = name
            country.official_name = official_name
            country.iso_alpha_2_code = iso_alpha_2_code
            country.iso_numeric_code = iso_numeric_code
    session.commit()
