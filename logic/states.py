from aiogram.dispatcher.filters.state import State, StatesGroup


class NameGroup(StatesGroup):
    query = State()
    SEO_queries = State()
    range_search = State()
    price_category = State()


class User(StatesGroup):
    name = State()
    email = State()
    phone_number = State()


class Admin(StatesGroup):
    tg_id_to_add = State()
    tg_id_to_delete = State()


class TrendGraph(StatesGroup):
    category_selection = State()
    view_selection = State()
    value_selection = State()
    date_1_selection = State()
    date_2_selection = State()
