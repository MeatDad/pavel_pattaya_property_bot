# keyboards/filters_kb.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Areas (районы)
AREAS = [
    "Central Pattaya","South Pattaya","North Pattaya","Pratumnak",
    "Jomtien","Wongamat","Naklua","East Pattaya"
]

PROPERTY_TYPES = ["Condo","House","Villa","Townhome","Land"]

BUY_PRICE_BUTTONS = [
    ("0–2M", "0-2000000"),
    ("2–4M", "2000000-4000000"),
    ("4–6M", "4000000-6000000"),
    ("6–10M", "6000000-10000000"),
    ("10M+", "10000000-")
]

RENT_PRICE_BUTTONS = [
    ("0–10K", "0-10000"),
    ("10–20K", "10000-20000"),
    ("20–40K", "20000-40000"),
    ("40–70K", "40000-70000"),
    ("70K+", "70000-")
]

BEDROOMS = [("Studio", "0"), ("1", "1"), ("2", "2"), ("3+", "3")]

POPULAR_FEATURES = [
    ("Pool", "pool"),
    ("Sea View", "sea_view"),
    ("High Floor", "high_floor"),
    ("Corner Unit", "corner"),
    ("Brand New", "brand_new")
]

# Helpers to build keyboards
def main_filters_kb(mode: str, selected: dict) -> InlineKeyboardMarkup:
    """
    mode: "buy" or "rent"
    selected: dict of current selections to show in labels (optional)
    """
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(text="💰 Цена", callback_data=f"{mode}:price"),
        InlineKeyboardButton(text="🛏 Спальни", callback_data=f"{mode}:bedrooms"),
    )
    kb.add(
        InlineKeyboardButton(text="🏘 Тип", callback_data=f"{mode}:type"),
        InlineKeyboardButton(text="📍 Район", callback_data=f"{mode}:area"),
    )
    kb.add(
        InlineKeyboardButton(text="⚙️ More", callback_data=f"{mode}:more"),
        InlineKeyboardButton(text="♻️ Сбросить", callback_data=f"{mode}:reset"),
    )
    # Show results button (active always, server will check)
    kb.add(InlineKeyboardButton(text="🔎 Показать результаты", callback_data=f"{mode}:show"))
    return kb

def price_kb(mode: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = BUY_PRICE_BUTTONS if mode == "buy" else RENT_PRICE_BUTTONS
    for label, val in buttons:
        kb.insert(InlineKeyboardButton(text=label, callback_data=f"{mode}:price:{val}"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back"))
    return kb

def bedrooms_kb(mode: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    for label, val in BEDROOMS:
        kb.insert(InlineKeyboardButton(text=label, callback_data=f"{mode}:bed:{val}"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back"))
    return kb

def type_kb(mode: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    for t in PROPERTY_TYPES:
        kb.insert(InlineKeyboardButton(text=t, callback_data=f"{mode}:type:{t}"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back"))
    return kb

def area_kb(mode: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    for a in AREAS:
        kb.insert(InlineKeyboardButton(text=a, callback_data=f"{mode}:area:{a}"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back"))
    return kb

def more_kb(mode: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    for label, key in POPULAR_FEATURES:
        kb.insert(InlineKeyboardButton(text=label, callback_data=f"{mode}:feat:{key}"))
    kb.add(InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back"))
    kb.add(InlineKeyboardButton(text="🔎 Показать результаты", callback_data=f"{mode}:show"))
    return kb

def summary_kb(mode: str) -> InlineKeyboardMarkup:
    # small nav keyboard shown with the summary
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(InlineKeyboardButton(text="Изменить фильтры", callback_data=f"{mode}:open"),
           InlineKeyboardButton(text="🔎 Показать результаты", callback_data=f"{mode}:show"))
    return kb
