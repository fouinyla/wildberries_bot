from aiogram import types
from .utils import callback


def admin_start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Количество пользователей в БД'))
    markup.insert(types.KeyboardButton('Полная выгрузка из БД'))
    markup.add(types.KeyboardButton('Рассылка на всех пользователей'))
    markup.insert(types.KeyboardButton('Добавить админа'))
    markup.insert(types.KeyboardButton('Удалить админа'))
    markup.insert(types.KeyboardButton('Поисковой запрос'))
    markup.insert(types.KeyboardButton('Сбор SEO ядра'))
    markup.insert(types.KeyboardButton('Поиск по ранжированию'))
    # markup.insert(types.KeyboardButton('Получить график'))
    markup.insert(types.KeyboardButton('Ценовая сегментация'))
    markup.insert(types.KeyboardButton('Как пользоваться ботом'))
    return markup


def start_menu_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Поисковой запрос'))
    markup.insert(types.KeyboardButton('Сбор SEO ядра'))
    markup.insert(types.KeyboardButton('Поиск по ранжированию'))
    # markup.insert(types.KeyboardButton('Получить график'))
    markup.insert(types.KeyboardButton('Ценовая сегментация'))
    markup.insert(types.KeyboardButton('Как пользоваться ботом'))
    return markup


def confirmation_mailing_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.insert(types.KeyboardButton('Да, отправляй'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


def not_subscribed_markup():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Я подписался(-лась)'))
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
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('Собрать SEO повторно'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


def another_card_position_search_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('Ввести запрос повторно'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


# def another_trend_graph_markup():
#     markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     markup.add(types.KeyboardButton('Получить другой график'))
#     markup.insert(types.KeyboardButton('Назад в главное меню'))
#     return markup

    
def another_price_segmentation_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('Узнать ценовую сегментацию повторно'))
    markup.insert(types.KeyboardButton('Назад в главное меню'))
    return markup


def inline_categories_markup(categories, cat_id=None, prev_page=False, next_page=False, back_to=False, select=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if select:
        markup.add(
            types.InlineKeyboardButton(
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
            types.InlineKeyboardButton(
                category["name"],
                callback_data=callback(
                    dict(
                        a="PCK",
                        d=category["id"]
                    )
                )
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            ("⬅️" if prev_page else "❌"),
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
        ),
        types.InlineKeyboardButton(
            ("➡️" if next_page else "❌"),
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
    )

    markup.add(
        types.InlineKeyboardButton(
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
        ),
        types.InlineKeyboardButton(
            "В главное меню",
            callback_data=callback(
                dict(
                    a="ABR"
                )
            )
        )
    )
    return markup
