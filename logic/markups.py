from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from .utils import callback
from const.const import MPSTATS_TRENDS, MPSTATS_SECTIONS


def admin_start_menu_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(KeyboardButton('Поисковой запрос'))
    markup.insert(KeyboardButton('Сбор SEO ядра'))
    markup.insert(KeyboardButton('Поиск по ранжированию'))
    markup.insert(KeyboardButton('Получить график'))
    markup.insert(KeyboardButton('Ценовая сегментация'))
    markup.insert(KeyboardButton('Продажи по артикулу'))
    markup.insert(KeyboardButton('Как пользоваться ботом'))
    markup.insert(KeyboardButton('Функции админа'))
    return markup


def admin_menu_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(KeyboardButton('Количество пользователей в БД'))
    markup.insert(KeyboardButton('Полная выгрузка из БД'))
    markup.insert(KeyboardButton('Добавить админа'))
    markup.insert(KeyboardButton('Удалить админа'))
    markup.insert(KeyboardButton('Рассылка на всех пользователей'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def start_menu_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(KeyboardButton('Поисковой запрос'))
    markup.insert(KeyboardButton('Сбор SEO ядра'))
    markup.insert(KeyboardButton('Поиск по ранжированию'))
    markup.insert(KeyboardButton('Получить график'))
    markup.insert(KeyboardButton('Ценовая сегментация'))
    markup.insert(KeyboardButton('Продажи по артикулу'))
    markup.insert(KeyboardButton('Как пользоваться ботом'))
    return markup


def back_to_admin_menu_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(KeyboardButton('Назад в меню админа'))
    return markup


def confirmation_mailing_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(KeyboardButton('Да, отправляй'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def not_subscribed_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(KeyboardButton('Я подписался(-лась)'))
    return markup


def back_to_name_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(KeyboardButton('Назад к вводу имени'))
    return markup


def back_to_email_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(KeyboardButton('Назад к вводу почты'))
    return markup


def back_to_phone_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(KeyboardButton('Назад к вводу телефона'))
    return markup


def back_to_main_menu_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def go_to_seo_markup():
    markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(KeyboardButton('Сбор SEO ядра'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def another_search_query_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton('Ввести поисковой запрос повторно'))
    markup.insert(KeyboardButton('Сбор SEO ядра'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def another_seo_building_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton('Собрать SEO повторно'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def another_card_position_search_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton('Ввести запрос повторно'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


# _______________________клавиатуры для выдачи графиков_______________________
def graph_view_selection_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for section in MPSTATS_SECTIONS:
        markup.insert(KeyboardButton(section))
    markup.add(KeyboardButton('Назад в главное меню'))
    return markup


def graph_value_selection_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for value in MPSTATS_TRENDS:
        markup.insert(KeyboardButton(value))
    markup.add(KeyboardButton('Назад в главное меню'))
    return markup


def another_trend_graph_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton('Получить другой график'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup
# ___________________окончание клавиатур для выдачи графиков___________________


def another_price_segmentation_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton('Узнать ценовую сегментацию повторно'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def another_month_sales_markup():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton('Узнать продажи по артикулу повторно'))
    markup.insert(KeyboardButton('Назад в главное меню'))
    return markup


def inline_categories_markup(categories, cat_id=None, prev_page=False,
                             next_page=False, back_to=False, select=True):
    PREV_BUTTON = InlineKeyboardButton(
        "⬅️",
        callback_data=callback(
            (
                dict(
                    a="PRV",
                    d=str(cat_id),
                    p=prev_page
                ) if prev_page
                else (
                    dict(
                        a='.'
                    )
                )
            )
        )
    )

    NEXT_BUTTON = InlineKeyboardButton(
        "➡️",
        callback_data=callback(
            (
                dict(
                    a="NXT",
                    d=str(cat_id),
                    p=next_page
                ) if next_page
                else (
                    dict(
                        a='.'
                    )
                )
            )
        )
    )

    BACK_BUTTON = InlineKeyboardButton(
        ("Назад" if back_to else "❌"),
        callback_data=callback(
            (
                dict(
                    a="PCK",
                    d=back_to,
                ) if back_to
                else dict(
                    a='.'
                )
            )
        )
    )

    MAIN_MENU_BUTTON = InlineKeyboardButton(
        "В главное меню",
        callback_data=callback(
            dict(
                a="ABR"
            )
        )
    )

    markup = InlineKeyboardMarkup(row_width=2)
    if select:
        markup.add(
            InlineKeyboardButton(
                "⬇️Выбрать весь раздел⬇️",
                callback_data=callback(
                    dict(
                        a="SCT",
                        d=cat_id
                    )
                )
            )
        )

    for category in categories:
        markup.add(
            InlineKeyboardButton(
                category["name"],
                callback_data=callback(
                    dict(
                        a="PCK",
                        d=category["id"]
                    )
                )
            )
        )

    row = []
    if prev_page and next_page:
        markup.add(PREV_BUTTON, NEXT_BUTTON)
        if back_to:
            row.append(BACK_BUTTON)
        row.append(MAIN_MENU_BUTTON)
        markup.add(*row)
    else:
        if prev_page:
            row.append(PREV_BUTTON)
        if back_to:
            row.append(BACK_BUTTON)
        else:
            row.append(MAIN_MENU_BUTTON)
        if next_page:
            row.append(NEXT_BUTTON)
        markup.add(*row)

        if back_to:
            markup.add(MAIN_MENU_BUTTON)

    return markup
