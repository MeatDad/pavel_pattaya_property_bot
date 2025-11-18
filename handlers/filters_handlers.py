from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from keyboards.filters_kb import (
    main_filters_kb, price_kb, bedrooms_kb, type_kb, area_kb, more_kb, summary_kb
)
from services.parser import parse_properties

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.warning(">>> FILTERS HANDLER LOADED AND ACTIVE <<<")

router = Router()


# --- 1. Вход в фильтры ("Купить" / "Арендовать") ---
@router.message(F.text.in_(["🏠 Купить", "🏖 Арендовать"]))
async def enter_filters(message: types.Message, state: FSMContext):
    logger.info("enter_filters triggered for user %s text=%s", message.from_user.id, message.text)
    text = message.text
    mode = "buy" if "Купить" in text else "rent"

    await state.set_data({
        "mode": mode,
        "location": None,
        "min_price": None,
        "max_price": None,
        "bedrooms": None,
        "property_type": None,
        "features": []
    })

    await message.answer(
        "Выберите параметры поиска:",
        reply_markup=main_filters_kb(mode, {})
    )


# --- 2. Универсальный обработчик всех callback-кнопок ---
@router.callback_query()
async def handle_callbacks(query: types.CallbackQuery, state: FSMContext):
    data = query.data
    if not data:
        return

    parts = data.split(":")
    mode = parts[0]                     # buy / rent
    action = parts[1] if len(parts) > 1 else None

    # Берём или создаём фильтры
    user_data = await state.get_data()
    if not user_data:
        await state.set_data({
            "mode": mode,
            "location": None, "min_price": None, "max_price": None,
            "bedrooms": None, "property_type": None, "features": []
        })
        user_data = await state.get_data()

    # --- Навигация ---
    if action in ["open", "back"]:
        await query.message.edit_text(
            "Выберите параметры поиска:",
            reply_markup=main_filters_kb(mode, user_data)
        )
        await query.answer()
        return

    # --- Переход в подменю ---
    if action == "price" and len(parts) == 2:
        await query.message.edit_text("Выберите диапазон цены:", reply_markup=price_kb(mode))
        await query.answer()
        return

    if action == "bedrooms" and len(parts) == 2:
        await query.message.edit_text("Выберите количество спален:", reply_markup=bedrooms_kb(mode))
        await query.answer()
        return

    if action == "type" and len(parts) == 2:
        await query.message.edit_text("Выберите тип недвижимости:", reply_markup=type_kb(mode))
        await query.answer()
        return

    if action == "area" and len(parts) == 2:
        await query.message.edit_text("Выберите район:", reply_markup=area_kb(mode))
        await query.answer()
        return

    if action == "more" and len(parts) == 2:
        await query.message.edit_text("Дополнительные фильтры:", reply_markup=more_kb(mode))
        await query.answer()
        return

    # --- Установка значений ---
    if action == "price" and len(parts) == 3:
        rng = parts[2]  # "0-2000000"
        min_s, max_s = rng.split("-")
        min_v = int(min_s) if min_s else None
        max_v = int(max_s) if max_s else None

        await state.update_data(min_price=min_v, max_price=max_v)
        user = await state.get_data()

        await query.message.edit_text(
            f"Цена установлена: {rng}\n\nТекущие фильтры: {user}",
            reply_markup=summary_kb(mode)
        )
        await query.answer("Цена установлена")
        return

    if action == "bed" and len(parts) == 3:
        bedrooms = parts[2]
        await state.update_data(bedrooms=bedrooms)

        user = await state.get_data()
        await query.message.edit_text(
            f"Спальни: {bedrooms}\n\nТекущие фильтры: {user}",
            reply_markup=summary_kb(mode)
        )
        await query.answer()
        return

    if action == "type" and len(parts) == 3:
        ptype = parts[2]
        await state.update_data(property_type=ptype)

        user = await state.get_data()
        await query.message.edit_text(
            f"Тип: {ptype}\n\nТекущие фильтры: {user}",
            reply_markup=summary_kb(mode)
        )
        await query.answer()
        return

    if action == "area" and len(parts) == 3:
        area = parts[2]
        await state.update_data(location=area)

        user = await state.get_data()
        await query.message.edit_text(
            f"Район: {area}\n\nТекущие фильтры: {user}",
            reply_markup=summary_kb(mode)
        )
        await query.answer()
        return

    # --- Доп. фильтры (toggle) ---
    if action == "feat" and len(parts) == 3:
        feat = parts[2]
        data_now = await state.get_data()

        feats = data_now.get("features", [])
        if feat in feats:
            feats.remove(feat)
        else:
            feats.append(feat)

        await state.update_data(features=feats)
        user = await state.get_data()

        await query.message.edit_text(
            f"Фильтры: {user}",
            reply_markup=main_filters_kb(mode, user)
        )
        await query.answer("Изменено")
        return

    # --- Сброс ---
    if action == "reset":
        await state.set_data({
            "mode": mode,
            "location": None, "min_price": None, "max_price": None,
            "bedrooms": None, "property_type": None, "features": []
        })

        await query.message.edit_text(
            "Фильтры сброшены.",
            reply_markup=main_filters_kb(mode, {})
        )
        await query.answer("Сброшено")
        return

    # --- Показ результатов ---
    if action == "show":
        filters = await state.get_data()
        section = "🏠 Купить" if mode == "buy" else "🏖 Арендовать"

        await query.message.edit_text("Идёт поиск по выбранным фильтрам... 🔎")

        results = parse_properties(section, filters)

        if not results:
            await query.message.answer("Не найдено объектов по указанным фильтрам.")
            await query.answer()
            return

        for item in results:
            caption = (
                f"<b>{item['title']}</b>\n"
                f"💰 {item['price']}\n"
                f"📍 {item.get('location', '')}\n"
                f"<a href='{item['link']}'>Подробнее</a>"
            )
            if item.get("img"):
                await query.message.answer_photo(item["img"], caption=caption)
            else:
                await query.message.answer(caption)

        await query.answer("Готово")
        return

    # fallback
    await query.answer()
