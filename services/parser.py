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

def _build_search_url(section: str, filters: Dict) -> str:
    """
    section: either '🏠 Купить' or '🏖 Арендовать' (or other short names)
    filters: dict from FSM state, example:
      {
        "mode": "buy",
        "min_price": 0,
        "max_price": 2000000,
        "bedrooms": "1",
        "property_type": "Condo",
        "location": "Central Pattaya",
        "features": ["pool", "sea_view"]
      }
    Returns full URL to request (first page).
    """
    mode = filters.get("mode", "buy") if filters else ("buy" if "Купить" in section else "rent")
    # site endpoints guess: use 'sale' for buy, 'rent' for rent (observed earlier)
    if mode == "buy":
        endpoint = "/public/units/sale"
    else:
        endpoint = "/public/units/rent"

    params = {
        # keep empty defaults expected by site
        "country": "",
        "text": "",  # optional free text
        "price": "",
    }

    # map prices (site seems to use min_price & max_price numeric)
    if filters:
        min_p = filters.get("min_price")
        max_p = filters.get("max_price")
        if min_p is not None:
            params["min_price"] = str(min_p)
        if max_p is not None:
            params["max_price"] = str(max_p)

        # bedrooms -> parameter 'bed'
        bedrooms = filters.get("bedrooms")
        if bedrooms:
            # if bedrooms was "Studio"/"0" etc — site probably expects bed=1 etc
            try:
                # if numeric string -> use directly
                bed_val = int(bedrooms)
                params["bed"] = str(bed_val)
            except Exception:
                # map Studio->0, "1"->1 etc
                if bedrooms.lower().startswith("studio"):
                    params["bed"] = "0"
                else:
                    # fallback: try to extract digit
                    import re
                    m = re.search(r"\d+", str(bedrooms))
                    if m:
                        params["bed"] = m.group(0)

        # property type mapping: site used `type2[]` in example; we will try both name and numeric code
        ptype = filters.get("property_type")
        if ptype:
            # Some sites use numeric codes; try using text param 'type' or 'type2[]'
            # We'll set 'type2[]' to property type name (site may accept human-readable too)
            params["type2[]"] = ptype

        # location -> free-text 'text' parameter is used in sample url
        location = filters.get("location")
        if location:
            params["text"] = str(location)

        # features -> could be encoded differently per site; we'll set 'feature' param as comma list
        features = filters.get("features", [])
        if features:
            params["feature"] = ",".join(features)

    # urlencode but preserve [] in keys
    # build manually to preserve repeated parameters if needed
    q_parts = []
    for k, v in params.items():
        if v is None or v == "":
            # keep param with empty value maybe necessary for site; we will include empty string
            q_parts.append(f"{quote_plus(k)}=")
        else:
            q_parts.append(f"{quote_plus(k)}={quote_plus(str(v))}")
    query = "&".join(q_parts)
    url = f"{BASE}{endpoint}?{query}"
    return url

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
