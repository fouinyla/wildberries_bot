from aiogram.dispatcher.filters.state import State, StatesGroup


class NameGroup(StatesGroup):
    query = State()
    SEO_queries = State()


class User(StatesGroup):
    name = State()
    email = State()
    phone_number = State()
