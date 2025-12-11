# services/parser.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
import time
from typing import Dict, List, Optional

BASE = "https://enlightproperty.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PavelPattayaBot/1.0; +https://enlightproperty.com)"
}

# Маппинги: кнопки -> параметры сайта
PRICE_MAP_BUY = {
    "0-2000000": ("min_price", "max_price"),
    # We'll set actual values later in build_query
}
# helper: if filter gives "0-2000000", we put min_price=0, max_price=2000000

# встроим в services/parser.py

# карта типов недвижимости: текст -> код
PROPERTY_TYPE_MAP = {
    "Condo": "1",
    "House": "2",
    "Villa": "3",
    "Townhome": "4",
    "Land": "5"
}

def _build_search_url(section: str, filters: dict) -> str:
    mode = filters.get("mode", "buy")
    if mode == "buy":
        endpoint = "/public/units/sale"
    else:
        endpoint = "/public/units/rent"

    params = {}

    # строка поиска (город / район)
    text = filters.get("location")
    if text:
        params["text"] = text

    # минимальная и максимальная цена
    if filters.get("min_price") is not None:
        params["min_price"] = str(filters["min_price"])
    if filters.get("max_price") is not None:
        params["max_price"] = str(filters["max_price"])

    # спальни
    if filters.get("bedrooms"):
        params["bed"] = str(filters["bedrooms"])

    # ванны
    if filters.get("bathrooms"):
        params["bathroom"] = str(filters["bathrooms"])

    # тип недвижимости (используем числовой код)
    ptype = filters.get("property_type")
    if ptype:
        code = PROPERTY_TYPE_MAP.get(ptype)
        if code:
            params["type2[]"] = code

    # дополнительные фильтры через текст (fallback)
    features = filters.get("features")
    if features:
        params["text"] = params.get("text", "") + " " + " ".join(features)

    # принудительно добавляем пустые, если почему-то нужны
    params.setdefault("country", "")

    query = urlencode(params, doseq=True)
    return f"{BASE}{endpoint}?{query}"


def _parse_listing_block(block) -> Optional[Dict]:
    try:
        # title
        title_tag = block.select_one("h2.product-title a, .product-title a")
        title = title_tag.get_text(strip=True) if title_tag else ""

        # link
        link = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
        if link and link.startswith("/"):
            link = BASE + link
        # price
        price_tag = block.select_one(".product-price span, .product-price")
        price = price_tag.get_text(strip=True) if price_tag else ""

        # image
        img_tag = block.select_one("img")
        img = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
        if img and img.startswith("/"):
            img = BASE + img

        # location
        loc_tag = block.select_one(".product-img-location ul li a, .product-img-location ul li, .product-img-location")
        location = loc_tag.get_text(strip=True) if loc_tag else ""

        # bedrooms / bathrooms / type / size
        # collect property-info-text occurrences
        prop_texts = [t.get_text(strip=True) for t in block.select(".property-info-text")]
        bedrooms = None
        property_type = None
        size = None
        for t in prop_texts:
            if "Bedroom" in t or "Bedrooms" in t or "Bed" in t:
                bedrooms = t.replace("Bedroom", "").strip()
            if any(tp.lower() in t.lower() for tp in ["Condo", "House", "Villa", "Townhome", "Land"]):
                property_type = t.strip()
            if "sq.m" in t or "sqm" in t:
                size = t

        uid = None
        # code like CPTHCS0047 shown in product-description p
        code_tag = block.select_one(".product-description p")
        if code_tag:
            uid = code_tag.get_text(strip=True)

        return {
            "title": title,
            "link": link,
            "price": price,
            "img": img,
            "location": location,
            "bedrooms": bedrooms,
            "property_type": property_type,
            "size": size,
            "uid": uid,
        }
    except Exception:
        return None

def parse_properties(section: str, filters: Dict = None, pages: int = 1) -> List[Dict]:
    """
    section: text label like "🏠 Купить" or "🏖 Арендовать" (used to infer mode if filters none)
    filters: dict (see _build_search_url)
    pages: how many pages to fetch (1 by default)
    Returns: list of dicts with property info
    """
    results = []
    # build url for first page based on filters
    url = _build_search_url(section, filters or {})
    # some sites require small delay and pagination param e.g. &page=2
    for page in range(1, pages + 1):
        page_url = url
        if page > 1:
            # append page param
            if "page=" in page_url:
                page_url = page_url.replace("page=1", f"page={page}")
            else:
                page_url = f"{page_url}&page={page}"

        try:
            r = requests.get(page_url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                break
            soup = BeautifulSoup(r.text, "lxml")
            # find product blocks (robust selectors)
            blocks = soup.select(".ltn__product-item, .ltn__product-item-4, .product-item, .ltn__property-item")
            if not blocks:
                # try fallback: look for articles / list items
                blocks = soup.select(".product-img")  # minimal
            for b in blocks:
                item = _parse_listing_block(b)
                if item:
                    results.append(item)
            # polite pause
            time.sleep(0.2)
        except Exception:
            break
    return results
