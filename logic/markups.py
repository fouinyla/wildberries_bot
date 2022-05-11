from aiogram import types


def admin_start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Количество пользователей в БД'))
    markup.insert(types.KeyboardButton('Полная выгрузка из БД')) 
    markup.insert(types.KeyboardButton('Поисковой запрос'))
    markup.insert(types.KeyboardButton('Сбор SEO ядра'))
    markup.add(types.KeyboardButton('Как пользоваться ботом'))
    return markup


def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Поисковой запрос'))
    markup.insert(types.KeyboardButton('Сбор SEO ядра'))
    markup.add(types.KeyboardButton('Как пользоваться ботом'))
    return markup


def back_to_name_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Назад к вводу имени'))
    return markup


def back_to_email_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Назад к вводу почты'))
    return markup


def back_to_phone_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Назад к вводу телефона'))
    return markup


def back_to_main_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


def go_to_seo_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Сбор SEO ядра'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


def another_search_query_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('Ввести поисковой запрос повторно'))
    markup.insert(types.KeyboardButton('Сбор SEO ядра'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


def another_seo_building_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Собрать SEO повторно'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup
