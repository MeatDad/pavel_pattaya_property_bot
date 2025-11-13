import requests
from bs4 import BeautifulSoup
from config import BASE_URL

def parse_properties(section: str, limit: int = 5):
    urls = {
        "🏠 Купить": f"{BASE_URL}/public/units/sale",
        "🏖 Арендовать": f"{BASE_URL}/public/units/rent",
        "🌆 Проекты": f"{BASE_URL}/projects",
        "🏢 Продать недвижимость": f"{BASE_URL}/sell-your-property-here",
        "📅 Бронирование": f"{BASE_URL}/booking",
    }

    url = urls.get(section)
    if not url:
        return []

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    listings = []

    # Карточки объектов
    for item in soup.select(".ltn__product-item")[:limit]:
        title_tag = item.select_one(".product-title a")
        price_tag = item.select_one(".product-price span")
        img_tag = item.select_one(".product-img img")

        title = title_tag.get_text(strip=True) if title_tag else "Без названия"
        price = price_tag.get_text(strip=True) if price_tag else "Цена по запросу"
        link = title_tag["href"] if title_tag and title_tag.get("href") else None
        img = img_tag["src"] if img_tag and img_tag.get("src") else None

        if link and not link.startswith("http"):
            link = BASE_URL + link

        listings.append({
            "title": title,
            "price": price,
            "link": link,
            "img": img
        })

    return listings
