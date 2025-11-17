# services/parser.py
import requests
from bs4 import BeautifulSoup
from config import BASE_URL
from urllib.parse import urlencode

def build_search_url(section: str, filters: dict):
    """
    section: "🏠 Купить" or "🏖 Арендовать"
    filters: dict from FSMContext
    Returns URL string
    """
    base = BASE_URL
    params = {}
    if "Купить" in section:
        path = "/public/units/sale"
    else:
        path = "/public/units/rent"

    # map filters to query params used by site
    if filters.get("location"):
        params["text"] = filters["location"]
    if filters.get("min_price") is not None:
        params["min_price"] = str(filters["min_price"])
    if filters.get("max_price") is not None and filters["max_price"] != "":
        params["max_price"] = str(filters["max_price"])
    if filters.get("bedrooms") is not None:
        params["bed"] = str(filters["bedrooms"])
    if filters.get("property_type"):
        # site might use type2[] param for types; adapt if needed
        params["type2[]"] = filters["property_type"]
    # features mapping (depends on site; we will try include features in text)
    if filters.get("features"):
        # append features as text search (fallback)
        params["text"] = (params.get("text","") + " " + " ".join(filters["features"])).strip()

    query = urlencode(params, doseq=True)
    return f"{base}{path}?{query}" if query else f"{base}{path}"

def parse_properties(section: str, filters: dict = None, limit: int = 6):
    """
    section: message text or "buy"/"rent".
    filters: dict from state (optional)
    """
    if filters is None:
        filters = {}

    url = build_search_url(section, filters)
    try:
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        print("Parser: request failed:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    listings = []
    for item in soup.select(".ltn__product-item")[:limit]:
        title_tag = item.select_one(".product-title a")
        price_tag = item.select_one(".product-price span")
        img_tag = item.select_one(".product-img img")
        loc_tag = item.select_one(".product-img-location ul li a")

        title = title_tag.get_text(strip=True) if title_tag else "Без названия"
        price = price_tag.get_text(strip=True) if price_tag else "Цена по запросу"
        link = title_tag["href"] if title_tag and title_tag.get("href") else None
        img = img_tag["src"] if img_tag and img_tag.get("src") else None
        location = loc_tag.get_text(strip=True) if loc_tag else ""

        if link and not link.startswith("http"):
            link = BASE_URL + link

        listings.append({
            "title": title,
            "price": price,
            "link": link,
            "img": img,
            "location": location
        })
    return listings
