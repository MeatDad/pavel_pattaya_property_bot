# services/parser.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

BASE = "https://enlightproperty.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PavelPattayaBot/1.0)"
}

PROPERTY_TYPE_MAP = {
    "Condo": "1",
    "House": "2",
    "Villa": "3",
    "Townhome": "4",
    "Land": "5"
}


# ---------- PRICE HELPERS ----------

def parse_price(text: str) -> Optional[int]:
    """
    Converts price text like:
    '฿1,250,000', 'From ฿950,000', '1.2M', 'Price on request'
    into integer THB or None
    """
    if not text:
        return None

    t = text.lower()

    if "request" in t:
        return None

    t = (
        t.replace("from", "")
        .replace("฿", "")
        .replace(",", "")
        .strip()
    )

    if "m" in t:
        try:
            return int(float(t.replace("m", "")) * 1_000_000)
        except ValueError:
            return None

    digits = "".join(c for c in t if c.isdigit())
    return int(digits) if digits else None


def price_in_range(price: Optional[int], min_p: Optional[int], max_p: Optional[int]) -> bool:
    if price is None:
        return False
    if min_p is not None and price < min_p:
        return False
    if max_p is not None and price > max_p:
        return False
    return True


# ---------- URL BUILDER ----------

def _build_search_url(filters: dict) -> str:
    mode = filters.get("mode", "buy")
    endpoint = "/public/units/sale" if mode == "buy" else "/public/units/rent"

    params = {
        "country": "",
        "price": "",
        "text": "พัทยา",
        "city": "พัทยา",
        "province": "ชลบุรี",
    }

    # bedrooms
    if filters.get("bedrooms"):
        params["bed"] = filters["bedrooms"]

    # property type
    ptype = filters.get("property_type")
    if ptype and ptype in PROPERTY_TYPE_MAP:
        params["type[]"] = PROPERTY_TYPE_MAP[ptype]

    query = urlencode(params, doseq=True)
    url = f"{BASE}{endpoint}?{query}"

    logger.warning("BUILT URL: %s", url)
    return url


# ---------- PARSER ----------

def _parse_listing_block(block) -> Optional[Dict]:
    try:
        title_tag = block.select_one("h2.product-title a, .product-title a")
        title = title_tag.get_text(strip=True) if title_tag else ""

        link = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
        if link.startswith("/"):
            link = BASE + link

        price_tag = block.select_one(".product-price span, .product-price")
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        price_value = parse_price(price_text)

        img_tag = block.select_one("img")
        img = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
        if img and img.startswith("/"):
            img = BASE + img

        loc_tag = block.select_one(".product-img-location")
        location = loc_tag.get_text(strip=True) if loc_tag else ""

        return {
            "title": title,
            "link": link,
            "price": price_text,
            "price_value": price_value,
            "img": img,
            "location": location,
        }
    except Exception as e:
        logger.exception("Parse error")
        return None


# ---------- MAIN ENTRY ----------

def parse_properties(section: str, filters: Dict = None, pages: int = 1) -> List[Dict]:
    filters = filters or {}
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")

    url = _build_search_url(filters)
    results = []

    for page in range(1, pages + 1):
        page_url = url if page == 1 else f"{url}&page={page}"

        r = requests.get(page_url, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.text, "lxml")
        blocks = soup.select(".ltn__property-item, .product-item")

        for b in blocks:
            item = _parse_listing_block(b)
            if not item:
                continue

            logger.warning(
                "PRICE CHECK: raw=%r parsed=%r min=%r max=%r",
                item["price"], item["price_value"], min_price, max_price
            )

            if not price_in_range(item["price_value"], min_price, max_price):
                continue

            results.append(item)

        time.sleep(0.3)

    return results
