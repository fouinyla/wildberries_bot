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
        if message.text == 'Сбор SEO ядра':
            markup = markups.back_to_main_menu_markup()
            text = 'Супер! Теперь пришлите мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
            await state.set_state(states.NameGroup.SEO_queries)
        else:
            async with state.proxy() as data:
                data['query'] = message.text
            hints = wildberries.get_hints_from_wb(data['query'])
            if hints == 204:
                markup = markups.back_to_main_menu_markup()
                text = 'По вашему запросу продолжений на Wildberries не найдено. Попробуйте другой запрос.'
            elif not hints:
                markup = markups.go_to_seo_markup()
                text = 'Вы ввели конечный поисковый запрос.'
            else:
                markup = markups.go_to_seo_markup()
                text = '\n'.join(hints)
        return dict(text=text, markup=markup)

    async def building_seo_core(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'Супер! Теперь пришлите мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
        await state.set_state(states.NameGroup.SEO_queries)
        return dict(text=text, markup=markup)

    async def building_seo_result(self, message, state):
        async with state.proxy() as data:
            data['SEO_queries'] = message.text
            text = f'Вы прислали следующие запросы:\n{data["SEO_queries"]}'
        markup = markups.back_to_main_menu_markup()
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
