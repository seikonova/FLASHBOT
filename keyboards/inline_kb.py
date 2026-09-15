from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


choose_product_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👟 Кроссовки", callback_data="product_shoes")],
        [InlineKeyboardButton(text="👕 Одежда", callback_data="product_clothing")],
        [InlineKeyboardButton(text="🎒 Аксессуары", callback_data="product_accessories")],
    ]
)


# Размеры обуви в сантиметрах
choose_shoes_size_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="22.5 см", callback_data="size_22.5"),
            InlineKeyboardButton(text="23 см", callback_data="size_23"),
            InlineKeyboardButton(text="23.5 см", callback_data="size_23.5"),
        ],
        [
            InlineKeyboardButton(text="24 см", callback_data="size_24"),
            InlineKeyboardButton(text="24.5 см", callback_data="size_24.5"),
            InlineKeyboardButton(text="25 см", callback_data="size_25"),
        ],
        [
            InlineKeyboardButton(text="25.5 см", callback_data="size_25.5"),
            InlineKeyboardButton(text="26 см", callback_data="size_26"),
            InlineKeyboardButton(text="26.5 см", callback_data="size_26.5"),
        ],
        [
            InlineKeyboardButton(text="27 см", callback_data="size_27"),
            InlineKeyboardButton(text="27.5 см", callback_data="size_27.5"),
            InlineKeyboardButton(text="28 см", callback_data="size_28"),
        ],
        [
            InlineKeyboardButton(text="28.5 см", callback_data="size_28.5"),
            InlineKeyboardButton(text="29 см", callback_data="size_29"),
            InlineKeyboardButton(text="29.5 см", callback_data="size_29.5"),
        ],
        [
            InlineKeyboardButton(text="30 см", callback_data="size_30"),
            InlineKeyboardButton(text="30.5 см", callback_data="size_30.5"),
            InlineKeyboardButton(text="31 см", callback_data="size_31"),
        ],
    ]
)


choose_clothing_size_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="XS", callback_data="size_XS"),
            InlineKeyboardButton(text="S", callback_data="size_S"),
        ],
        [
            InlineKeyboardButton(text="M", callback_data="size_M"),
            InlineKeyboardButton(text="L", callback_data="size_L"),
        ],
        [
            InlineKeyboardButton(text="XL", callback_data="size_XL"),
            InlineKeyboardButton(text="2XL", callback_data="size_2XL"),
        ],
        [
            InlineKeyboardButton(text="3XL", callback_data="size_3XL"),
        ],
    ]
)


confirm_order_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order")],
    ]
)


def admin_order_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔵 В работу", callback_data=f"order_processing_{order_id}")],
            [InlineKeyboardButton(text="✉️ Написать пользователю", callback_data=f"admin_message_{order_id}")],
            [
                InlineKeyboardButton(text="🟢 Выполнен", callback_data=f"order_completed_{order_id}"),
                InlineKeyboardButton(text="🔴 Отменить", callback_data=f"order_cancel_{order_id}")
            ]
        ]
    )


def admin_order_processing_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Написать пользователю", callback_data=f"admin_message_{order_id}")],
            [
                InlineKeyboardButton(text="🟢 Выполнен", callback_data=f"order_completed_{order_id}"),
                InlineKeyboardButton(text="🔴 Отменить", callback_data=f"order_cancel_{order_id}")
            ]
        ]
    )


def admin_order_completed_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Написать пользователю", callback_data=f"admin_message_{order_id}")]
        ]
    )


def admin_order_cancelled_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✉️ Написать пользователю", callback_data=f"admin_message_{order_id}")]
        ]
    )


def admin_messages_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_messages_refresh")]
        ]
    )
