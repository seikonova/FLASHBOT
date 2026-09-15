import html
import aiosqlite

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import keyboards.reply_kb as rkb
import keyboards.inline_kb as ikb
import config as cfg

from database import DBFunctions, DB_FILE
from handlers.state import OrderState
from handlers.admin import notify_admin_new_order

cmd_router = Router()


# =========================
# START
# =========================

@cmd_router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        text=cfg.start_text,
        reply_markup=rkb.start_kb
    )


# =========================
# НАЧАЛО ЗАКАЗА
# =========================

@cmd_router.message(F.text == "🛒Сделать заказ")
async def cmd_order(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(OrderState.name)

    sent_message = await message.answer(
        "🛍 <b>Оформление заказа</b>\n\n"
        "Давайте оформим ваш заказ.\n\n"
        "👤 Введите ваше имя:",
        parse_mode="HTML"
    )

    await state.update_data(
        sent_message=sent_message.message_id
    )

    try:
        await message.delete()
    except Exception:
        pass


# =========================
# ИМЯ
# =========================

@cmd_router.message(OrderState.name)
async def get_name(message: Message, state: FSMContext):
    if not message.text:
        return

    name = message.text.strip()

    if len(name) < 2:
        await message.answer(
            "❌ Имя слишком короткое.\n\n"
            "Пожалуйста, введите ваше имя ещё раз."
        )
        return

    await state.update_data(name=name)

    data = await state.get_data()
    bot_message_id = data.get("sent_message")

    try:
        await message.delete()
    except Exception:
        pass

    await state.set_state(OrderState.product_type)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=(
            "🛍 <b>Оформление заказа</b>\n\n"
            f"👤 Имя: <b>{html.escape(name)}</b>\n\n"
            "📦 <b>Выберите категорию товара:</b>"
        ),
        parse_mode="HTML",
        reply_markup=ikb.choose_product_kb
    )


# =========================
# КРОССОВКИ
# =========================

@cmd_router.callback_query(
    OrderState.product_type,
    F.data == "product_shoes"
)
async def handle_shoes_selection(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    await state.update_data(
        product_type="Кроссовки"
    )

    await state.set_state(OrderState.size)

    await callback.message.edit_text(
        "👟 <b>Кроссовки</b>\n\n"
        "📏 Выберите необходимый размер:",
        parse_mode="HTML",
        reply_markup=ikb.choose_shoes_size_kb
    )


# =========================
# ОДЕЖДА
# =========================

@cmd_router.callback_query(
    OrderState.product_type,
    F.data == "product_clothing"
)
async def handle_clothing_selection(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    await state.update_data(
        product_type="Одежда"
    )

    await state.set_state(OrderState.size)

    await callback.message.edit_text(
        "👕 <b>Одежда</b>\n\n"
        "📏 Выберите необходимый размер:",
        parse_mode="HTML",
        reply_markup=ikb.choose_clothing_size_kb
    )


# =========================
# АКСЕССУАРЫ
# =========================

@cmd_router.callback_query(
    OrderState.product_type,
    F.data == "product_accessories"
)
async def handle_accessories_selection(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    await state.update_data(
        product_type="Аксессуары",
        size=None
    )

    await state.set_state(OrderState.model)

    await callback.message.edit_text(
        "🎒 <b>Аксессуары</b>\n\n"
        "🏷 <b>Введите название модели:</b>\n\n"
        "Например: AirPods Pro 2",
        parse_mode="HTML"
    )


# =========================
# РАЗМЕР
# =========================

@cmd_router.callback_query(
    OrderState.size,
    F.data.startswith("size_")
)
async def handle_size_selection(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    size = callback.data.replace("size_", "")

    await state.update_data(
        size=size
    )

    await state.set_state(OrderState.model)

    data = await state.get_data()
    product_type = data.get("product_type")

    await callback.message.edit_text(
        f"📦 <b>{html.escape(product_type)}</b>\n\n"
        f"📏 Размер: <b>{html.escape(size)}</b>\n\n"
        "🏷 <b>Введите название модели:</b>\n\n"
        "Например: Nike Air Max 95",
        parse_mode="HTML"
    )


# =========================
# НАЗВАНИЕ МОДЕЛИ
# =========================

@cmd_router.message(OrderState.model)
async def get_model(
    message: Message,
    state: FSMContext
):
    if not message.text:
        return

    model = message.text.strip()

    if len(model) < 2:
        await message.answer(
            "❌ Название модели слишком короткое.\n\n"
            "Введите название модели ещё раз."
        )
        return

    await state.update_data(
        model=model
    )

    data = await state.get_data()
    bot_message_id = data.get("sent_message")
    product_type = data.get("product_type")
    size = data.get("size")

    size_text = size if size else "Не требуется"

    try:
        await message.delete()
    except Exception:
        pass

    await state.set_state(OrderState.comment)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=(
            "🏷 <b>Название модели</b>\n\n"
            f"📦 Товар: <b>{html.escape(product_type)}</b>\n"
            f"📏 Размер: <b>{html.escape(size_text)}</b>\n"
            f"🏷 Модель: <b>{html.escape(model)}</b>\n\n"
            "💬 <b>Теперь напишите комментарий к заказу.</b>\n\n"
            "Например:\n"
            "• цвет\n"
            "• ссылка на товар\n"
            "• дополнительные пожелания\n"
            "• другие характеристики\n\n"
            "Если комментарий не нужен — напишите <b>«Нет»</b>."
        ),
        parse_mode="HTML"
    )


# =========================
# КОММЕНТАРИЙ
# =========================

@cmd_router.message(OrderState.comment)
async def get_comment(
    message: Message,
    state: FSMContext
):
    if not message.text:
        return

    comment = message.text.strip()

    if comment.lower() == "нет":
        comment = None

    await state.update_data(
        comment=comment
    )

    data = await state.get_data()

    bot_message_id = data.get("sent_message")
    name = data.get("name")
    product_type = data.get("product_type")
    size = data.get("size")
    model = data.get("model")

    size_text = size if size else "Не требуется"
    comment_text = comment if comment else "Нет"

    try:
        await message.delete()
    except Exception:
        pass

    await state.set_state(OrderState.confirm)

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_message_id,
        text=(
            "🛒 <b>Проверьте ваш заказ</b>\n\n"
            "━━━━━━━━━━━━━━\n\n"
            f"👤 Имя: <b>{html.escape(name)}</b>\n"
            f"📦 Товар: <b>{html.escape(product_type)}</b>\n"
            f"📏 Размер: <b>{html.escape(size_text)}</b>\n"
            f"🏷 Модель: <b>{html.escape(model)}</b>\n"
            f"💬 Комментарий: <b>{html.escape(comment_text)}</b>\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "Всё верно?"
        ),
        parse_mode="HTML",
        reply_markup=ikb.confirm_order_kb
    )


# =========================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# =========================

async def get_order_id_by_number(order_number: str) -> int | None:
    """Получает ID заказа по его уникальному номеру."""
    async with aiosqlite.connect(DB_FILE) as conn:
        cursor = await conn.execute(
            "SELECT id FROM orders WHERE order_number = ? LIMIT 1",
            (order_number,)
        )
        row = await cursor.fetchone()
        return row[0] if row else None


# =========================
# ПОДТВЕРЖДЕНИЕ ЗАКАЗА
# =========================

@cmd_router.callback_query(
    OrderState.confirm,
    F.data == "confirm_order"
)
async def confirm_order(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    data = await state.get_data()

    name = data.get("name")
    product_type = data.get("product_type")
    size = data.get("size")
    model = data.get("model")
    comment = data.get("comment")

    # Username пользователя из Telegram
    username = callback.from_user.username

    try:
        # Создаём заказ
        order_number = await DBFunctions.generate_order_number(
            user_id=callback.from_user.id,
            name=name,
            product_type=product_type,
            size=size,
            model=model,
            comment=comment,
            username=username
        )

    except TypeError:
        # Совместимость со старой версией DBFunctions,
        # если в generate_order_number пока нет параметра username.
        order_number = await DBFunctions.generate_order_number(
            user_id=callback.from_user.id,
            name=name,
            product_type=product_type,
            size=size,
            model=model,
            comment=comment
        )

    except Exception as e:
        print(
            f"❌ Ошибка создания заказа: "
            f"{type(e).__name__}: {e}"
        )

        await callback.message.edit_text(
            "❌ <b>Не удалось оформить заказ</b>\n\n"
            "Произошла ошибка при сохранении заказа.\n"
            "Попробуйте ещё раз позже.",
            parse_mode="HTML"
        )

        await state.clear()
        return

    # Находим ID созданного заказа по номеру.
    # Он нужен для inline-кнопок администратора.
    order_id = await get_order_id_by_number(order_number)

    # Уведомляем администратора сразу после создания заказа.
    if order_id is not None:
        try:
            await notify_admin_new_order(
                callback.bot,
                order_id
            )
        except Exception as e:
            # Ошибка уведомления админа не должна ломать оформление заказа.
            print(
                f"❌ Ошибка уведомления администратора: "
                f"{type(e).__name__}: {e}"
            )
    else:
        print(
            f"⚠️ Не удалось получить ID заказа "
            f"{order_number} для уведомления администратора."
        )

    size_text = size if size else "Не требуется"

    await callback.message.edit_text(
        "✅ <b>Заказ оформлен</b>\n\n"
        "Ваш заказ успешно принят.\n\n"
        "━━━━━━━━━━━━━━\n\n"
        f"🧾 Номер заказа: <b>#{html.escape(order_number)}</b>\n"
        f"📦 Товар: <b>{html.escape(product_type)}</b>\n"
        f"📏 Размер: <b>{html.escape(size_text)}</b>\n"
        f"🏷 Модель: <b>{html.escape(model)}</b>\n\n"
        "━━━━━━━━━━━━━━\n\n"
        "Мы свяжемся с вами после обработки заказа.\n\n"
        "Спасибо, что выбираете <b>FLASH</b>.",
        parse_mode="HTML"
    )

    await state.clear()


# =========================
# ОТМЕНА ЗАКАЗА
# =========================

@cmd_router.callback_query(
    F.data == "cancel_order"
)
async def cancel_order(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer("Заказ отменён")

    await state.clear()

    await callback.message.edit_text(
        "❌ <b>Заказ отменён</b>\n\n"
        "Оформление заказа было отменено.\n\n"
        "Вы можете оформить новый заказ в любое время.",
        parse_mode="HTML"
    )


# =========================
# ЛИЧНЫЙ КАБИНЕТ
# =========================

@cmd_router.message(F.text == "👤 Личный кабинет")
async def profile(message: Message):
    await message.answer(
        "👤 <b>Личный кабинет</b>\n\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=rkb.profile_kb
    )


# =========================
# МОИ ЗАКАЗЫ
# =========================

@cmd_router.message(F.text == "📦 Мои заказы")
async def my_orders(message: Message):
    orders = await DBFunctions.get_user_orders(
        message.from_user.id
    )

    if not orders:
        await message.answer(
            "📦 <b>Мои заказы</b>\n\n"
            "У вас пока нет оформленных заказов.",
            parse_mode="HTML",
            reply_markup=rkb.profile_kb
        )
        return

    text = "📦 <b>Мои заказы</b>\n\n"

    for order in orders:
        order_number = order["order_number"]
        product_type = order["product_type"]
        model = order["model"]
        status = order["status"]

        status_text = {
            "new": "🟡 Новый",
            "processing": "🔵 В обработке",
            "completed": "🟢 Выполнен",
            "cancelled": "🔴 Отменён"
        }.get(status, "⚪ Неизвестно")

        text += (
            f"🧾 <b>#{html.escape(order_number)}</b>\n"
            f"📦 Товар: {html.escape(product_type)}\n"
            f"🏷 Модель: {html.escape(model or 'Не указана')}\n"
            f"📌 Статус: {status_text}\n\n"
        )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=rkb.profile_kb
    )


# =========================
# ГЛАВНОЕ МЕНЮ
# =========================

@cmd_router.message(F.text == "◀️ Главное меню")
async def main_menu(message: Message):
    await message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=rkb.start_kb
    )

# =========================
# ОТВЕТ ПОЛЬЗОВАТЕЛЯ АДМИНИСТРАТОРУ
# =========================

@cmd_router.message(F.reply_to_message)
async def user_reply_to_admin(message: Message):
    """
    Пользователь отвечает через обычный Telegram Reply
    на сообщение, которое ранее отправил администратор.
    """

    if not message.text:
        return

    replied_message_id = message.reply_to_message.message_id

    order = await DBFunctions.get_order_by_admin_message_id(
        replied_message_id
    )

    if not order:
        return

    username = message.from_user.username
    username_text = (
        f"@{html.escape(username)}"
        if username
        else "Не указан"
    )

    text = (
        "📩 <b>Ответ пользователя</b>\n\n"
        f"🧾 Заказ: <b>#{html.escape(order['order_number'])}</b>\n"
        f"👤 Имя: <b>{html.escape(order['name'])}</b>\n"
        f"📱 Username: <b>{username_text}</b>\n"
        f"🆔 ID: <code>{message.from_user.id}</code>\n\n"
        "💬 <b>Сообщение:</b>\n"
        f"{html.escape(message.text)}"
    )

    try:
        await message.bot.send_message(
            chat_id=cfg.ADMIN_ID,
            text=text,
            parse_mode="HTML"
        )

        await message.answer(
            "✅ <b>Сообщение отправлено администратору.</b>",
            parse_mode="HTML"
        )

    except Exception as e:
        print(
            f"❌ Ошибка отправки ответа администратору: "
            f"{type(e).__name__}: {e}"
        )
        await message.answer(
            "❌ Не удалось отправить сообщение. "
            "Попробуйте ещё раз."
        )

    try:
        await message.delete()
    except Exception:
        pass

