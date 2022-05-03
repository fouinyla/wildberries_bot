from datetime import datetime
from email import message
from aiogram import types
from db.db_connector import Database
import const.phrases as phrases
from const.const import *
from . import markups
from logic.notification_service import Notification_Service
from . import states
from . import wildberries as wb
from . import mpstats


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.notification = Notification_Service(
            bot=self.bot,
        )

    async def command_start(self, message, state):
        await state.finish()
        result = self.db.get_user(message.from_user.id)
        name = message.from_user.first_name
        markup = None
        text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB. \n\nВведите ваше имя'
        if result:
            text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
            markup = markups.start_menu_markup()
        else:
            await state.set_state(states.User.name)
        return dict(text=text, markup=markup)

    async def message_name_state(self, message, state):
        text = 'Введите свой e-mail'
        async with state.proxy() as data:
            data['name'] = message.text
        await state.set_state(states.User.email)
        return dict(text=text)

    async def message_email_state(self, message, state):
        text = 'Введите свой номер телефона'
        async with state.proxy() as data:
            data['email'] = message.text
        await state.set_state(states.User.phone_number)
        return dict(text=text)

    async def message_phone_number_state(self, message, state):
        text = 'Выберите команду'
        markup = markups.start_menu_markup()
        async with state.proxy() as data:
            data['phone_number'] = message.text
            self.db.add_user(message.from_user.id, message.from_user.first_name,
                             data['name'], data['email'], data['phone_number'])
        await state.finish()
        return dict(text=text, markup=markup)

    async def search_query(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'Пожалуйста, введите свой поисковой запрос.'
        await state.set_state(states.NameGroup.query)
        return dict(text=text, markup=markup)

    async def giving_hints(self, message, state):
        if message.text == 'Сбор SEO ядра':
            markup = markups.back_to_main_menu_markup()
            text = 'Супер! Теперь отправьте мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
            await state.set_state(states.NameGroup.SEO_queries)
            return dict(text=text, markup=markup)

        async with state.proxy() as data:
            data['query'] = message.text

        user = self.db.get_user(tg_id=message.from_user.id)
        if user:
            self.db.add_search_query(
                search_query=message.text,
                user_id=user['id']
            )

        hints = wb.get_hints(data['query'])
        if hints:
            markup = markups.go_to_seo_markup()
            text = '\n'.join(hints)
        elif hints == [] or (hints is None and wb.product_exists(data['query'])):
            markup = markups.go_to_seo_markup()
            text = 'Вы ввели конечный поисковый запрос.'
        else:
            markup = markups.back_to_main_menu_markup()
            text = 'По вашему запросу продолжений на Wildberries не найдено. Попробуйте другой запрос.'
        return dict(text=text, markup=markup)

    async def building_seo_core(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'Супер! Теперь отправьте мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
        await state.set_state(states.NameGroup.SEO_queries)
        return dict(text=text, markup=markup)

    async def waiting_seo_result(self, message, state):
        async with state.proxy() as data:
            data['SEO_queries'] = message.text
        text = f'Подготавливаем excel-файл. Это может занять до 1 минуты (в зависимости от количества запросов).'
        markup = markups.back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    async def building_seo_result(self, message, state):
        async with state.proxy() as data:
            path_to_excel = mpstats.get_SEO(data['SEO_queries'], str(message.from_user.id))
            await message.answer_document(
                    document=open(path_to_excel, 'rb')
                )
            user = self.db.get_user(tg_id=message.from_user.id)
            if user:
                query_for_SEO = str(message.text).replace('\n', '; ')
                self.db.add_SEO_query(
                    query_for_SEO=query_for_SEO,
                    tg_id=message.from_user.id
                )
        return None

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
