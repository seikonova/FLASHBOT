import html

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

import config as cfg
import keyboards.inline_kb as ikb
import keyboards.reply_kb as rkb

from database import DBFunctions
from handlers.state import AdminState


admin_router = Router()


# =========================================================
# ПРОВЕРКА АДМИНА
# =========================================================

def is_admin(user_id: int) -> bool:
    return user_id == cfg.ADMIN_ID


# =========================================================
# УВЕДОМЛЕНИЕ АДМИНИСТРАТОРА О НОВОМ ЗАКАЗЕ
# =========================================================

async def notify_admin_new_order(bot, order_id: int):
    order = await DBFunctions.get_order(order_id)

    if not order:
        return

    username = order["username"] if "username" in order.keys() else None
    username_text = f"@{html.escape(username)}" if username else "Не указан"

    text = (
        "🆕 <b>Новый заказ</b>\n\n"
        f"🧾 Номер: <b>#{html.escape(order['order_number'])}</b>\n"
        f"👤 Имя: <b>{html.escape(order['name'])}</b>\n"
        f"📱 Username: <b>{username_text}</b>\n"
        f"🆔 ID: <code>{order['user_id']}</code>\n\n"
        f"📦 Товар: <b>{html.escape(order['product_type'])}</b>\n"
        f"🏷 Модель: <b>{html.escape(order['model'] or 'Не указана')}</b>\n"
        f"📏 Размер: <b>{html.escape(order['size'] or 'Не требуется')}</b>\n"
        f"💬 Комментарий: <b>{html.escape(order['comment'] or 'Нет')}</b>\n\n"
        f"📅 Создан: {html.escape(order['created_at'])}"
    )

    await bot.send_message(
        chat_id=cfg.ADMIN_ID,
        text=text,
        parse_mode="HTML",
        reply_markup=ikb.admin_order_kb(order_id)
    )


# =========================================================
# АДМИН-ПАНЕЛЬ
# =========================================================

@admin_router.message(Command("admin"))
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🔐 <b>Панель администратора</b>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=rkb.admin_kb
    )


@admin_router.message(F.text == "🔐 Админ-панель")
async def admin_panel_button(message: Message):

    if not is_admin(message.from_user.id):
        return

    await message.answer(
        "🔐 <b>Панель администратора</b>\n\n"
        "Выберите нужный раздел:",
        parse_mode="HTML",
        reply_markup=rkb.admin_kb
    )


# =========================================================
# СООБЩЕНИЯ
# =========================================================

@admin_router.message(F.text == "💬 Сообщения")
async def admin_messages(message: Message):
    if not is_admin(message.from_user.id):
        return

    messages = await DBFunctions.get_admin_messages(50)

    if not messages:
        await message.answer(
            "💬 <b>Сообщения</b>\n\n"
            "Сообщений пока нет.",
            parse_mode="HTML",
            reply_markup=rkb.admin_kb
        )
        return

    await message.answer(
        f"💬 <b>Последние сообщения: {len(messages)}</b>",
        parse_mode="HTML"
    )

    for item in messages:
        username = item["username"]
        username_text = f"@{html.escape(username)}" if username else "Не указан"
        order_number = item["order_number"] or "Без заказа"
        message_text = item["message_text"] or "Без текста"

        text = (
            f"💬 <b>Сообщение #{item['id']}</b>\n\n"
            f"🧾 Заказ: <b>#{html.escape(order_number)}</b>\n"
            f"👤 {html.escape(item['name'] or 'Не указано')}\n"
            f"📱 Username: <b>{username_text}</b>\n"
            f"🆔 ID: <code>{item['user_id']}</code>\n"
            f"📅 {html.escape(item['created_at'])}\n\n"
            f"📝 {html.escape(message_text)}"
        )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=ikb.admin_order_kb(item["order_id"])
        )


# =========================================================
# НОВЫЕ ЗАКАЗЫ
# =========================================================

@admin_router.message(F.text == "📦 Новые заказы")
async def new_orders(message: Message):

    if not is_admin(message.from_user.id):
        return

    orders = await DBFunctions.get_new_orders()

    if not orders:

        await message.answer(
            "📦 <b>Новые заказы</b>\n\n"
            "Новых заказов нет.",
            parse_mode="HTML",
            reply_markup=rkb.admin_kb
        )

        return

    await message.answer(
        f"📦 <b>Новые заказы: {len(orders)}</b>",
        parse_mode="HTML"
    )

    for order in orders:

        order_number = order["order_number"]
        name = order["name"]
        username = order["username"] if "username" in order.keys() else None
        product_type = order["product_type"]
        model = order["model"]
        size = order["size"]
        comment = order["comment"]

        username_text = (
            f"@{html.escape(username)}"
            if username
            else "Не указан"
        )

        text = (
            f"🧾 <b>#{html.escape(order_number)}</b>\n\n"
            f"👤 Имя: <b>{html.escape(name)}</b>\n"
            f"📱 Username: <b>{username_text}</b>\n"
            f"🆔 ID: <code>{order['user_id']}</code>\n\n"
            f"📦 Товар: <b>{html.escape(product_type)}</b>\n"
            f"🏷 Модель: <b>{html.escape(model or 'Не указана')}</b>\n"
            f"📏 Размер: <b>{html.escape(size or 'Не требуется')}</b>\n"
            f"💬 Комментарий: "
            f"<b>{html.escape(comment or 'Нет')}</b>\n\n"
            f"📅 Создан: {html.escape(order['created_at'])}"
        )

        keyboard = ikb.admin_order_kb(order["id"])

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=keyboard
        )


# =========================================================
# ВСЕ ЗАКАЗЫ
# =========================================================

@admin_router.message(F.text == "📋 Все заказы")
async def all_orders(message: Message):

    if not is_admin(message.from_user.id):
        return

    orders = await DBFunctions.get_all_orders()

    if not orders:

        await message.answer(
            "📋 <b>Все заказы</b>\n\n"
            "Заказов пока нет.",
            parse_mode="HTML",
            reply_markup=rkb.admin_kb
        )

        return

    for order in orders:

        status_text = {
            "new": "🟡 Новый",
            "processing": "🔵 В обработке",
            "completed": "🟢 Выполнен",
            "cancelled": "🔴 Отменён"
        }.get(
            order["status"],
            "⚪ Неизвестно"
        )

        username = order["username"] if "username" in order.keys() else None
        username_text = (
            f"@{html.escape(username)}"
            if username
            else "Не указан"
        )

        text = (
            f"🧾 <b>#{html.escape(order['order_number'])}</b>\n\n"
            f"👤 {html.escape(order['name'])}\n"
            f"📱 Username: <b>{username_text}</b>\n"
            f"🆔 ID: <code>{order['user_id']}</code>\n"
            f"📦 {html.escape(order['product_type'])}\n"
            f"🏷 {html.escape(order['model'] or 'Не указана')}\n"
            f"📌 Статус: {status_text}"
        )

        await message.answer(
            text,
            parse_mode="HTML",
            reply_markup=ikb.admin_order_kb(order["id"])
        )


# =========================================================
# НАПИСАТЬ ПОЛЬЗОВАТЕЛЮ
# =========================================================

@admin_router.callback_query(
    F.data.startswith("admin_message_")
)
async def admin_message_user(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    order_id = int(
        callback.data.replace(
            "admin_message_",
            ""
        )
    )

    order = await DBFunctions.get_order(order_id)

    if not order:

        await callback.answer(
            "Заказ не найден",
            show_alert=True
        )

        return

    await state.set_state(
        AdminState.waiting_message
    )

    await state.update_data(
        order_id=order_id,
        user_id=order["user_id"]
    )

    await callback.answer()

    username = order["username"] if "username" in order.keys() else None
    username_text = f"@{html.escape(username)}" if username else "Не указан"

    await callback.message.answer(
        "✉️ <b>Сообщение пользователю</b>\n\n"
        f"Заказ: <b>#{html.escape(order['order_number'])}</b>\n"
        f"Username: <b>{username_text}</b>\n"
        f"Пользователь: <code>{order['user_id']}</code>\n\n"
        "Введите сообщение, которое нужно отправить:",
        parse_mode="HTML"
    )


# =========================================================
# ОТПРАВКА СООБЩЕНИЯ
# =========================================================

@admin_router.message(AdminState.waiting_message)
async def send_message_to_user(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    if not message.text:
        await message.answer(
            "❌ Пожалуйста, отправьте сообщение текстом."
        )
        return

    data = await state.get_data()

    order_id = data.get("order_id")
    user_id = data.get("user_id")

    order = await DBFunctions.get_order(order_id)

    if not order:

        await message.answer(
            "❌ Заказ не найден."
        )

        await state.clear()

        return

    try:

        sent_message = await message.bot.send_message(
            chat_id=user_id,
            text=(
                "📩 <b>Сообщение по вашему заказу</b>\n\n"
                f"🧾 Заказ: <b>#{html.escape(order['order_number'])}</b>\n\n"
                f"{html.escape(message.text)}\n\n"
                "↩️ <i>Ответьте на это сообщение через Reply, чтобы написать администратору.</i>"
            ),
            parse_mode="HTML"
        )

        await DBFunctions.save_admin_message(
            order_id=order_id,
            user_id=user_id,
            telegram_message_id=sent_message.message_id,
            message_text=message.text
        )

        await DBFunctions.save_admin_response(
            order_id,
            message.text
        )

        await message.answer(
            "✅ <b>Сообщение отправлено</b>\n\n"
            f"Пользователь получил сообщение "
            f"по заказу #{html.escape(order['order_number'])}.",
            parse_mode="HTML",
            reply_markup=rkb.admin_kb
        )

    except Exception as e:

        print(
            f"❌ Ошибка отправки сообщения: "
            f"{type(e).__name__}: {e}"
        )

        await message.answer(
            "❌ Не удалось отправить сообщение пользователю.\n\n"
            "Возможно, пользователь заблокировал бота."
        )

    await state.clear()


# =========================================================
# ВЗЯТЬ ЗАКАЗ В РАБОТУ
# =========================================================

@admin_router.callback_query(
    F.data.startswith("order_processing_")
)
async def order_processing(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    order_id = int(
        callback.data.replace(
            "order_processing_",
            ""
        )
    )

    order = await DBFunctions.get_order(order_id)

    if not order:

        await callback.answer(
            "Заказ не найден",
            show_alert=True
        )

        return

    await DBFunctions.update_order_status(
        order_id,
        "processing"
    )

    await callback.answer(
        "Заказ взят в работу"
    )

    await callback.message.edit_reply_markup(
        reply_markup=ikb.admin_order_processing_kb(
            order_id
        )
    )

    try:

        sent_message = await callback.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🔵 <b>Ваш заказ взят в работу</b>\n\n"
                f"🧾 Номер заказа: "
                f"<b>#{html.escape(order['order_number'])}</b>\n\n"
                "Мы уже занимаемся вашим заказом."
            ),
            parse_mode="HTML"
        )

        await DBFunctions.save_admin_message(
            order_id=order_id,
            user_id=order["user_id"],
            telegram_message_id=sent_message.message_id,
            message_text="Ваш заказ взят в работу"
        )

    except Exception as e:

        print(
            f"❌ Не удалось уведомить пользователя: {e}"
        )


# =========================================================
# ЗАКАЗ ВЫПОЛНЕН
# =========================================================

@admin_router.callback_query(
    F.data.startswith("order_completed_")
)
async def order_completed(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    order_id = int(
        callback.data.replace(
            "order_completed_",
            ""
        )
    )

    order = await DBFunctions.get_order(order_id)

    if not order:

        await callback.answer(
            "Заказ не найден",
            show_alert=True
        )

        return

    await DBFunctions.update_order_status(
        order_id,
        "completed"
    )

    await callback.answer(
        "Заказ отмечен как выполненный"
    )

    await callback.message.edit_reply_markup(
        reply_markup=ikb.admin_order_completed_kb(
            order_id
        )
    )

    try:

        sent_message = await callback.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🟢 <b>Ваш заказ выполнен</b>\n\n"
                f"🧾 Номер заказа: "
                f"<b>#{html.escape(order['order_number'])}</b>\n\n"
                "Спасибо, что выбираете <b>FLASH</b>."
            ),
            parse_mode="HTML"
        )

        await DBFunctions.save_admin_message(
            order_id=order_id,
            user_id=order["user_id"],
            telegram_message_id=sent_message.message_id,
            message_text="Ваш заказ выполнен"
        )

    except Exception as e:

        print(
            f"❌ Не удалось уведомить пользователя: {e}"
        )


# =========================================================
# ОТМЕНА
# =========================================================

@admin_router.callback_query(
    F.data.startswith("order_cancel_")
)
async def order_cancel(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    order_id = int(
        callback.data.replace(
            "order_cancel_",
            ""
        )
    )

    order = await DBFunctions.get_order(order_id)

    if not order:

        await callback.answer(
            "Заказ не найден",
            show_alert=True
        )

        return

    await DBFunctions.update_order_status(
        order_id,
        "cancelled"
    )

    await callback.answer(
        "Заказ отменён"
    )

    await callback.message.edit_reply_markup(
        reply_markup=ikb.admin_order_cancelled_kb(
            order_id
        )
    )

    try:

        sent_message = await callback.bot.send_message(
            chat_id=order["user_id"],
            text=(
                "🔴 <b>Ваш заказ отменён</b>\n\n"
                f"🧾 Номер заказа: "
                f"<b>#{html.escape(order['order_number'])}</b>\n\n"
                "Если у вас есть вопросы, "
                "напишите нам."
            ),
            parse_mode="HTML"
        )

        await DBFunctions.save_admin_message(
            order_id=order_id,
            user_id=order["user_id"],
            telegram_message_id=sent_message.message_id,
            message_text="Ваш заказ отменён"
        )

    except Exception as e:

        print(
            f"❌ Не удалось уведомить пользователя: {e}"
        )