from aiogram import types


def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Поисковой запрос")) # .row, .add, .insert
    markup.insert(types.KeyboardButton("Сбор SEO ядра"))
    return markup

def search_query_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup
