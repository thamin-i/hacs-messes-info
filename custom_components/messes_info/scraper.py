"""This module contains a function to scrape masses informations."""

import typing as t
from urllib.parse import quote

import aiohttp
import async_timeout
from bs4 import BeautifulSoup
from bs4.element import Tag
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import BASE_URL


def parse_mass_from_soup(article: Tag) -> t.Dict[str, str]:
    """Parse the mass details from an article tag.

    Args:
        article (Tag): HTML article tag containing mass details.

    Returns:
        t.Dict[str, str]: Dict of mass details.
    """
    return {
        "title": article.find_all("h3")[0].text.strip(),
        "subtitle": article.find_all("h4")[0].text.strip(),
        "picture": str(t.cast(Tag, article.find_all("img")[0])["src"] or ""),
        "start_date": str(
            t.cast(Tag, article.find_all("meta", {"itemprop": "startDate"})[0]).get(
                "content"
            )
        ),
        "street_address": article.find_all("span", {"itemprop": "streetAddress"})[
            0
        ].text.strip(),
        "postal_code": article.find_all("span", {"itemprop": "postalCode"})[
            0
        ].text.strip(),
        "address_locality": article.find_all("span", {"itemprop": "addressLocality"})[
            0
        ].text.strip(),
        "latitude": str(
            t.cast(Tag, article.find_all("meta", {"itemprop": "latitude"})[0]).get(
                "content"
            )
        ),
        "longitude": str(
            t.cast(Tag, article.find_all("meta", {"itemprop": "longitude"})[0]).get(
                "content"
            )
        ),
        "diocese": article.find_all("a", {"itemprop": "url"})[0].text.strip(),
        "info": article.find_all("i")[0].text.strip(),
    }


def parse_masses(html: str) -> t.Dict[str, t.Any]:
    """Parse the HTML content using BeautifulSoup.

    Args:
        html (str): HTML content to parse.

    Returns:
        t.Dict[str, t.Any]: Dict of masses with their details.
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    articles = soup.find_all("article", {"itemtype": "http://schema.org/Event"})
    masses: t.Dict[str, t.Any] = {}
    for article in articles:
        mass: t.Dict[str, str] = parse_mass_from_soup(t.cast(Tag, article))
        masses[f"{mass['title']}{mass['subtitle']}"] = mass
    print(f"Found {len(masses)} masses")
    return masses


async def scrape_masses(
    postal_code: str,
    church_name: str,
) -> t.Dict[str, t.Any]:
    """Scrape masses information from messes.info.

    Args:
        postal_code (str): Church postal code.
        church_name (str): Church name.

    Returns:
        t.Dict[str, t.Any]: Dict of masses with their details.
    """
    url: str = f"{BASE_URL}/horaires/{quote(church_name + ' ' + postal_code)}"
    try:
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html: str = await response.text()
                    return parse_masses(html)
    except Exception as exception:
        raise UpdateFailed(f"Error scraping page: {exception}") from exception
