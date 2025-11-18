# keyboards/filters_kb.py
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

AREAS = [
    "Central Pattaya", "South Pattaya", "North Pattaya", "Pratumnak",
    "Jomtien", "Wongamat", "Naklua", "East Pattaya"
]

PROPERTY_TYPES = ["Condo", "House", "Villa", "Townhome", "Land"]

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


# ----- Aiogram 3 совместимые клавиатуры -----

def main_filters_kb(mode: str, selected: dict) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💰 Цена", callback_data=f"{mode}:price"),
                InlineKeyboardButton(text="🛏 Спальни", callback_data=f"{mode}:bedrooms")
            ],
            [
                InlineKeyboardButton(text="🏘 Тип", callback_data=f"{mode}:type"),
                InlineKeyboardButton(text="📍 Район", callback_data=f"{mode}:area")
            ],
            [
                InlineKeyboardButton(text="⚙️ More", callback_data=f"{mode}:more"),
                InlineKeyboardButton(text="♻️ Сбросить", callback_data=f"{mode}:reset")
            ],
            [
                InlineKeyboardButton(text="🔎 Показать результаты", callback_data=f"{mode}:show")
            ]
        ]
    )


def price_kb(mode: str) -> InlineKeyboardMarkup:
    rows = []
    buttons = BUY_PRICE_BUTTONS if mode == "buy" else RENT_PRICE_BUTTONS

    for label, val in buttons:
        rows.append([
            InlineKeyboardButton(text=label, callback_data=f"{mode}:price:{val}")
        ])

    rows.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def bedrooms_kb(mode: str) -> InlineKeyboardMarkup:
    rows = []

    for label, val in BEDROOMS:
        rows.append([
            InlineKeyboardButton(text=label, callback_data=f"{mode}:bed:{val}")
        ])

    rows.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def type_kb(mode: str) -> InlineKeyboardMarkup:
    rows = []

    for t in PROPERTY_TYPES:
        rows.append([
            InlineKeyboardButton(text=t, callback_data=f"{mode}:type:{t}")
        ])

    rows.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def area_kb(mode: str) -> InlineKeyboardMarkup:
    rows = []

    for a in AREAS:
        rows.append([
            InlineKeyboardButton(text=a, callback_data=f"{mode}:area:{a}")
        ])

    rows.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def more_kb(mode: str) -> InlineKeyboardMarkup:
    rows = []

    for label, key in POPULAR_FEATURES:
        rows.append([
            InlineKeyboardButton(text=label, callback_data=f"{mode}:feat:{key}")
        ])

    rows.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data=f"{mode}:back")
    ])

    rows.append([
        InlineKeyboardButton(text="🔎 Показать результаты", callback_data=f"{mode}:show")
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def summary_kb(mode: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Изменить фильтры", callback_data=f"{mode}:open"),
                InlineKeyboardButton(text="🔎 Показать результаты", callback_data=f"{mode}:show")
            ]
        ]
    )
