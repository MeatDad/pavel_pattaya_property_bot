# handlers/filters_handlers.py
from aiogram import Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from keyboards.filters_kb import (
    main_filters_kb, price_kb, bedrooms_kb, type_kb, area_kb, more_kb, summary_kb
)
from services.parser import parse_properties
from aiogram import F

router = Router()

# Entry points: intercept reply keyboard messages "🏠 Купить" / "🏖 Арендовать"
@router.message(lambda msg: msg.text in ["🏠 Купить", "🏖 Арендовать"])
async def enter_filters(message: types.Message, state: FSMContext):
    text = message.text
    mode = "buy" if "Купить" in text else "rent"
    # initialize filter store for user in FSM
    await state.set_data({
        "mode": mode,
        "location": None,
        "min_price": None,
        "max_price": None,
        "bedrooms": None,
        "property_type": None,
        "features": []
    })
    await message.answer("Выберите параметры поиска:", reply_markup=main_filters_kb(mode, {}))

# callback handler generic
@router.callback_query()
async def handle_callbacks(query: types.CallbackQuery, state: FSMContext):
    data = query.data  # e.g., "buy:price:0-2000000" or "rent:show"
    if not data:
        return
    parts = data.split(":")
    mode = parts[0]  # buy / rent
    action = parts[1] if len(parts) > 1 else None

    user_data = await state.get_data() or {}
    # guard: if no session, initialize
    if not user_data:
        await state.set_data({"mode": mode, "location": None, "min_price": None, "max_price": None,
                              "bedrooms": None, "property_type": None, "features": []})
        user_data = await state.get_data()

    # Navigation
    if action == "open":
        await query.message.edit_text("Выберите параметры поиска:", reply_markup=main_filters_kb(mode, user_data))
        await query.answer()
        return
    if action == "back":
        await query.message.edit_text("Выберите параметры поиска:", reply_markup=main_filters_kb(mode, user_data))
        await query.answer()
        return
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

    # Setting values (price / bed / type / area / feat)
    if action == "price" and len(parts) == 3:
        rng = parts[2]  # "0-2000000" or "10000000-"
        min_s, max_s = rng.split("-")
        min_v = int(min_s) if min_s else None
        max_v = int(max_s) if max_s else None if max_s == "" else int(max_s)
        # update state
        await state.update_data(min_price=min_v, max_price=max_v)
        user = await state.get_data()
        await query.message.edit_text(f"Цена установлена: {parts[2]}\n\nТекущие фильтры: {user}", reply_markup=summary_kb(mode))
        await query.answer("Цена установлена")
        return

    if action == "bed" and len(parts) == 3:
        bedrooms = parts[2]
        await state.update_data(bedrooms=bedrooms)
        user = await state.get_data()
        await query.message.edit_text(f"Спальни: {bedrooms}\n\nТекущие фильтры: {user}", reply_markup=summary_kb(mode))
        await query.answer()
        return

    if action == "type" and len(parts) == 3:
        ptype = parts[2]
        await state.update_data(property_type=ptype)
        user = await state.get_data()
        await query.message.edit_text(f"Тип: {ptype}\n\nТекущие фильтры: {user}", reply_markup=summary_kb(mode))
        await query.answer()
        return

    if action == "area" and len(parts) == 3:
        area = parts[2]
        await state.update_data(location=area)
        user = await state.get_data()
        await query.message.edit_text(f"Район: {area}\n\nТекущие фильтры: {user}", reply_markup=summary_kb(mode))
        await query.answer()
        return

    if action == "feat" and len(parts) == 3:
        feat = parts[2]
        data_now = await state.get_data()
        feats = data_now.get("features", [])
        # toggle feature
        if feat in feats:
            feats.remove(feat)
        else:
            feats.append(feat)
        await state.update_data(features=feats)
        user = await state.get_data()
        await query.message.edit_text(f"Фильтры: {user}", reply_markup=main_filters_kb(mode, user))
        await query.answer("Изменено")
        return

    if action == "reset":
        await state.set_data({"mode": mode, "location": None, "min_price": None, "max_price": None,
                              "bedrooms": None, "property_type": None, "features": []})
        await query.message.edit_text("Фильтры сброшены.", reply_markup=main_filters_kb(mode, {}))
        await query.answer("Сброшено")
        return

    if action == "show":
        # prepare filters and call parser/listings
        filters = await state.get_data()
        section = "🏠 Купить" if mode == "buy" else "🏖 Арендовать"
        await query.message.edit_text("Идёт поиск по выбранным фильтрам... 🔎")
        # call parser
        results = parse_properties(section, filters)
        if not results:
            await query.message.answer("Не найдено объектов по указанным фильтрам.")
            await query.answer()
            return
        for item in results:
            caption = f"<b>{item['title']}</b>\n💰 {item['price']}\n📍 {item.get('location','')}\n<a href='{item['link']}'>Подробнее</a>"
            if item.get("img"):
                await query.message.answer_photo(item["img"], caption=caption, parse_mode="HTML")
            else:
                await query.message.answer(caption, parse_mode="HTML")
        await query.answer("Готово")
        return

    # fallback
    await query.answer()
