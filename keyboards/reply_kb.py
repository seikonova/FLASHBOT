from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛒Сделать заказ"),
            KeyboardButton(text="👤 Личный кабинет")
        ]
    ],
    resize_keyboard=True
)

profile_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Мои заказы")],
        [KeyboardButton(text="◀️ Главное меню")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Новые заказы")],
        [KeyboardButton(text="📋 Все заказы")],
        [KeyboardButton(text="💬 Сообщения")],
        [KeyboardButton(text="◀️ Главное меню")]
    ],
    resize_keyboard=True
)
