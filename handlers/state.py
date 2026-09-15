from aiogram.fsm.state import State, StatesGroup


class OrderState(StatesGroup):
    name = State()
    product_type = State()
    size = State()
    model = State()
    comment = State()
    confirm = State()


class AdminState(StatesGroup):
    waiting_message = State()


class UserReplyState(StatesGroup):
    waiting_message = State()