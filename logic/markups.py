from aiogram import types


def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Поисковой запрос"))
    markup.insert(types.KeyboardButton("Сбор SEO ядра"))
    markup.add(types.KeyboardButton("Прочее"))
    return markup

def search_query_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup

def giving_hints_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup

def building_seo_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup

def other_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Оплата"), types.KeyboardButton("FAQ"))
    markup.add(types.KeyboardButton("Назад в главное меню"))
    return markup

def bot_payment_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в меню прочее"))
    return markup

def FAQ_bar_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в меню прочее"))
    return markup