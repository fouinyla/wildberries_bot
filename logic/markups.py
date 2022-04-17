from aiogram import types


def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Поисковой запрос"))
    markup.insert(types.KeyboardButton("Сбор SEO ядра"))
    markup.add(types.KeyboardButton("Прочее"))
    return markup

def back_to_main_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup

def go_to_seo_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton("Сбор SEO ядра"))
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup

def other_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.row(types.KeyboardButton("Оплата"), types.KeyboardButton("FAQ"))
    markup.add(types.KeyboardButton("Назад в главное меню"))
    return markup

def back_to_other_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в меню прочее"))
    return markup

"""def giving_hints_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup

def building_seo_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton("Назад в главное меню"))
    return markup"""