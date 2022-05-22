from aiogram import types
from aiogram.utils.emoji import emojize
import datetime
from ..utils import *
from const.const import *
from const import phrases
from .. import time as _time_


async def action_create_location_filter():
    text = phrases.phrase_for_inline_calendar_select_location()
    markup = types.InlineKeyboardMarkup(width=1)
    for i, location in enumerate(LOCATIONS):
        row = []
        callback_data = callback(
            dict(
                a="FLR",
                l=i
            )
        )
        row.append(types.InlineKeyboardButton(location, callback_data=callback_data))
        markup.row(*row)
    markup.row(types.InlineKeyboardButton(
        "🔙 Назад",
        callback_data=callback(
            dict(
                a="ABR"
            )
        )
    ))
    return dict(
        text=emojize(text),
        markup=markup
    )


async def action_create_calendar_markup(location):
    text = phrases.phrase_for_inline_calendar_select_date()
    markup = types.InlineKeyboardMarkup(width=7)

    now = _time_.get_users_datetime()
    month = now.month
    data_ignore = callback(
        dict(
            a="IGNORE"
        )
    )

    # ? First row - Week Days
    next_week = now + datetime.timedelta(days=6)

    days_count = (datetime.date(next_week.year, next_week.month, 1) - datetime.date(now.year, now.month, 1)).days
    current_week_day = now.weekday()

    row = []
    for i, day in enumerate([*DAY_OF_WEEK_SHORT[current_week_day:], *DAY_OF_WEEK_SHORT[0:current_week_day]]):
        d = now.day + i
        if d > days_count:
            d = d - days_count
            month = next_week.month
        callback_data = callback(
            dict(
                a="DAY",
                y=_time_.get_users_datetime().year,
                m=month,
                d=d,
                l=location
            )
        )
        row.append(types.InlineKeyboardButton(day, callback_data=callback_data))
    markup.row(*row)

    # ? Second row - month and manage buttons
    row = []
    info_text = str(now.day)
    if not now.month == next_week.month:
        info_text += " " + SHORT_MONTHS[now.month - 1]
    info_text += " - " + str(next_week.day) + " " + SHORT_MONTHS[next_week.month - 1]

    row.append(types.InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=callback(
            dict(
                a="AFC"
            )
        )))
    row.append(types.InlineKeyboardButton(emojize(":spiral_calendar_pad: " + info_text), callback_data=data_ignore))
    markup.row(*row)

    return dict(text=emojize(text), markup=markup)


async def action_create_time_markup(data, db):
    print("data", data)
    d = datetime.date(data["y"], data["m"], data["d"])
    times = db.get_available_time(date=d, location=data["l"])
    markup = types.InlineKeyboardMarkup()
    row = []
    text = phrases.phrase_for_inline_calendar_select_time()
    for t in times:
        time_obj = t.strftime("%H:%M")
        callback_data = callback(
            dict(
                a="TM",
                m=data["m"],
                d=data["d"],
                l=data["l"],
                t=time_obj
            )
        )
        row.append(types.InlineKeyboardButton(time_obj, callback_data=callback_data))
    markup.row(*row)
    row = []
    row.append(types.InlineKeyboardButton(
        emojize(":back: Назад"),
        callback_data=callback(
            dict(
                a="FLR",
                l=data["l"]
            )
        )
    ))
    if not times:
        text = phrases.phrase_for_inline_calendar_select_time_empty()
    markup.row(*row)

    return dict(text=emojize(text), markup=markup)


async def action_book_training(query, data, db, ns):
    print("DATA", data)
    current_date = _time_.get_users_datetime().date()
    month = data["m"]
    year = _time_.get_year(month=month)
    d = datetime.date(year, data["m"], data["d"])
    t = datetime.datetime.strptime(data["t"], "%H:%M").time()
    is_booked = db.check_time_availability(date=d, time=t)

    tg_id = query.from_user.id
    text = ""
    markup = None
    popup_text = None
    notification = None
    training_id = None
    if not is_booked:
        user = db.get_user(tg_id=tg_id)
        is_booked_a_training = db.check_if_booked_today(tg_id=tg_id, date=d)
        if is_booked_a_training:
            popup_text = phrases.phrase_for_inline_calendar_book_training_if_user_booked_a_training_alert(
                data=dict(
                    time=is_booked_a_training["time"].strftime('%H:%M')
                )
            )
            markup = "SAME"
        else:
            training_id = db.book_training(tg_id=tg_id, date=d, time=t)
            if current_date == d:
                notification = dict(
                    date=d,
                    time=t,
                    user_tg_nickname="@"+query.from_user.username,
                    name=user["name"],
                    location=LOCATIONS[data["l"]]
                )

            text_part2 = await ns.generate_notification_to_user_about_booking_training(
                data=dict(
                    date=d,
                    time=t,
                    location=LOCATIONS[data["l"]]
                )
            )
            text = phrases.phrase_for_inline_calendar_book_training(
                data=dict(
                    day=str(data["d"]),
                    month=str(data["m"]),
                    time=str(data["t"]),
                    weekday=DAY_OF_WEEK_CONJUGATED[d.weekday()],
                    part2=text_part2
                )
            )
    else:
        data["y"] = year
        result = await action_create_time_markup(data=data, db=db)
        text = result["text"]
        markup = result["markup"]
        popup_text = phrases.phrase_for_inline_calendar_book_training_alert()

    return dict(
        text=emojize(text),
        markup=markup,
        notification=notification,
        popup_text=popup_text,
        training_id=training_id,
        tg_id=tg_id
    )


async def action_abort():
    text = phrases.phrase_for_main_menu()
    markup = None
    return dict(
        text=emojize(text),
        markup=markup
    )


async def action_abort_from_calendar():
    return await action_create_location_filter()
