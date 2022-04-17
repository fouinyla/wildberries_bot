from datetime import datetime
from email import message
from aiogram import types
from db.db_connector import Database
import const.phrases as phrases
from const.const import *
from . import markups
from logic.notification_service import Notification_Service
from . import states
from . import wildberries


class Controller:
    def __init__(self, bot):
        self.bot = bot
        #self.db = Database()
        self.notification = Notification_Service(
            bot=self.bot,
        )

    async def command_start(self, message, state):
        await state.finish()
        name = message.from_user.first_name
        markup = markups.start_menu_markup()
        text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
        return dict(text=text, markup=markup)


    async def search_query(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'Пожалуйста, введите свой поисковой запрос.'
        await state.set_state(states.NameGroup.query)
        return dict(text=text, markup=markup)


    async def giving_hints(self, message, state):
        async with state.proxy() as data:
            data['query'] = message.text
        response = wildberries.get_hints_from_wb(data['query'])
        markup = markups.go_to_seo_markup()
        text = '\n'.join(response)
        await state.finish()
        return dict(text=text, markup=markup)

    async def building_seo(self):
        markup = markups.back_to_main_menu_markup()
        text = 'Супер! Теперь напишите мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
        return dict(text=text, markup=markup)

    async def other_menu(self):
        markup = markups.other_menu_markup()
        text = 'Теперь выберите необходимую опцию.'
        return dict(text=text, markup=markup)

    async def bot_payment(self):
        markup = markups.back_to_other_menu_markup()
        text = 'Чтобы оплатить бота, необходимо ...'
        return dict(text=text, markup=markup)

    async def FAQ_bar(self):
        markup = markups.back_to_other_menu_markup()
        text = 'Как пользоваться нашим ботом:\n...\n...'
        return dict(text=text, markup=markup)

'''
    async def message_main_menu_buttons_click(self, message):
        text = phrases.phrase_for_answer_to_main_menu_buttons(
            data=dict(
                button_title=message.text
            )
        )
        return dict(text=text)

    async def message_main_menu_button_notification_click(self, message):
        await self.notification.notify_admins_about_some_event(
            data=dict(
                user_name=message.from_user.first_name,
                user_nickname=message.from_user.username,
                date=datetime.now().date,
                time=datetime.now().time,
            )
        )
        text = "Notification has been sent to admins"
        return dict(text=text)
'''