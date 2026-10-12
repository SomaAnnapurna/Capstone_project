import re
from typing import Iterable

import requests
from bs4 import BeautifulSoup, Tag

from Database import Country


SOURCE_URL = "https://www.scrapethissite.com/pages/simple/"


def _number(text: str, *, integer: bool) -> int | float:
    cleaned = text.replace(",", "").strip()
    

    match = re.search(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", cleaned)
    if not match:
        raise ValueError(f"Could not find a number in {text!r}")
    value = float(match.group(0))
    return int(value) if integer else value


def _value(block: Tag, selector: str, label: str) -> str:
    node = block.select_one(selector)
    if node is not None:
        value = node.get_text(" ", strip=True)
        # Scrape This Site includes the field label inside each span.
        return re.sub(rf"^{re.escape(label)}(?:\s*\([^)]*\))?\s*:\s*", "", value, flags=re.I).strip()
    text = block.get_text(" ", strip=True)
    match = re.search(rf"{re.escape(label)}\s*:?\s*([^|]+?)(?=\s+(?:Capital|Population|Area)\s*:|$)", text, re.I)
    if not match:
        raise ValueError(f"Missing {label} in country block")
    return match.group(1).strip()


def parse_countries(html: str, limit: int = 20) -> list[Country]:
    """Parse country cards and return at most ``limit`` normalized records."""
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.select("div.country")
    if not blocks:
        # Fallback for equivalent markup: country headings with the four fields.
        blocks = soup.select("section.country, article.country")
    countries: list[Country] = []
    for block in blocks[:limit]:
        name_node = block.select_one("h3.country-name, h3")
        if name_node is None:
            continue
        name = name_node.get_text(" ", strip=True)
        capital = _value(block, ".country-capital", "Capital")
        population = int(_number(_value(block, ".country-population", "Population"), integer=True))
        area = float(_number(_value(block, ".country-area", "Area"), integer=False))
        countries.append(Country(name=name, capital=None if capital.lower() == "none" else capital, population=population, area=area))
    if len(countries) < min(limit, len(blocks)):
        raise ValueError("The page structure changed; not all country records could be parsed")
    return countries


def fetch_countries(url: str = SOURCE_URL, limit: int = 20, timeout: float = 20.0) -> list[Country]:
    response = requests.get(url, timeout=timeout, headers={"User-Agent": "country-data-pipeline/1.0"})
    response.raise_for_status()
    return parse_countries(response.text, limit=limit)


def as_dicts(countries: Iterable[Country]) -> list[dict[str, object]]:
    return [country.to_dict() for country in countries]