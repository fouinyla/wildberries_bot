from db.db_connector import Database
from . import markups
from logic.notification_service import Notification_Service
from . import states
from . import wildberries as wb
from . import mpstats
from const.phrases import FAQ
import re
import os
from aiogram.utils.markdown import hlink


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.notification = Notification_Service(bot=self.bot)

    async def command_start(self, message, state):
        await state.finish()
        result = self.db.get_user(message.from_user.id)
        if result:
            name = message.from_user.first_name
            text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
            markup = markups.start_menu_markup()
        else:
            name = message.from_user.first_name
            text = f'Приветствую, {name}!\n' + \
                    'Это наш бот для улучшения твоей карточки на WB.\n' + \
                    'Для начала мы хотим узнать немного о тебе.\n' + \
                    'Пожалуйста, введи своё имя.'
            markup = None
            await state.set_state(states.User.name)
        return dict(text=text, markup=markup)

    async def message_name_state(self, message, state):
        name_pattern = r'[ёЁА-Яа-я- A-za-z]+'
        if re.fullmatch(name_pattern, message.text):
            async with state.proxy() as data:
                data['name'] = message.text
            text = 'Пожалуйста, введи свой e-mail'
            markup = markups.back_to_name_markup()
            await state.set_state(states.User.email)
        else:
            text = 'Не похоже на твоё имя. Введи что-то более корректное.'
            markup = None
        return dict(text=text, markup=markup)

    async def message_email_state(self, message, state):
        email_pattern = r'([A-Za-z0-9]+[\.\-\_])*[A-Za-z0-9]+@[A-Za-z0-9]+[A-Za-z0-9-]*[A-Za-z0-9]+(\.[A-Z|a-z]{2,})+'
        if re.fullmatch(email_pattern, message.text):
            async with state.proxy() as data:
                data['email'] = message.text
            text = 'Пожалуйста, введи свой номер телефона.'
            markup = markups.back_to_email_markup()
            await state.set_state(states.User.phone_number)
        elif message.text == 'Назад к вводу имени':
            text = 'Пожалуйста, введи своё имя.'
            markup = None
            await state.set_state(states.User.name)
        else:
            text = 'Не похоже на email. Введи что-то более корректное.'
            markup = markups.back_to_name_markup()
        return dict(text=text, markup=markup)

    async def message_phone_number_state(self, message, state):
        phone_pattern = re.compile(r'[0-9 \+\-\(\)]{7,}')
        # r'(\+7|8){1}[ \-\(]{0,1}[ \-\(]{0,1}\d{3}[ \-\)]{0,1}[ \-\)]{0,1}\d{3}[ \-]{0,1}\d{2}[ \-]{0,1}\d{2}')
        if re.fullmatch(phone_pattern, message.text):
            async with state.proxy() as data:
                data['phone_number'] = message.text
                self.db.add_user(message.from_user.id,
                                 message.from_user.username,
                                 data['name'],
                                 data['email'],
                                 data['phone_number'])
            await state.finish()
            text = 'Спасибо за информацию! Теперь можешь собрать SEO.'
            markup = markups.start_menu_markup()
        elif message.text == 'Назад к вводу почты':
            text = 'Пожалуйста, введи свой e-mail'
            markup = markups.back_to_name_markup()
            await state.set_state(states.User.email)
        else:
            text = 'Не похоже на номер телефона. Введите что-то более корректное.'
            markup = markups.back_to_email_markup()
        return dict(text=text, markup=markup)

    async def search_query(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'Пожалуйста, введите свой поисковой запрос.'
        await state.set_state(states.NameGroup.query)
        return dict(text=text, markup=markup)

    async def giving_hints(self, message, state):
        if message.text == 'Сбор SEO ядра':
            markup = markups.back_to_main_menu_markup()
            text = 'Отправьте мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
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
            text = '\n'.join(hints)
        elif hints == [] or (hints is None and wb.product_exists(data['query'])):
            text = 'Вы ввели конечный поисковый запрос.'
        else:
            text = 'По вашему запросу продолжений на Wildberries не найдено. Попробуйте другой запрос.'
        markup = markups.another_search_query_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def building_seo_core(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'Отправьте мне все поисковые запросы, с которых я соберу все SEO у лучших 100 карточек.\n(Каждый запрос с новой строки).'
        await state.set_state(states.NameGroup.SEO_queries)
        return dict(text=text, markup=markup)

    async def waiting_seo_result(self, message, state):
        async with state.proxy() as data:
            data['SEO_queries'] = message.text
        text = 'Подготавливаем excel-файл. Это может занять до 1 минуты (в зависимости от количества запросов).'
        markup = markups.back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    async def building_seo_result(self, message, state):   
        async with state.proxy() as data:
            path_to_excel, flag_all_empty_queries = mpstats.get_SEO(data['SEO_queries'])
            if not flag_all_empty_queries:
                await message.answer_document(document=open(path_to_excel, 'rb'))
                user = self.db.get_user(tg_id=message.from_user.id)
                if user:
                    query_for_SEO = str(message.text).replace('\n', '; ')
                    self.db.add_SEO_query(query_for_SEO=query_for_SEO,
                                          tg_id=message.from_user.id)
                text = 'SEO подготовлено!'
            else:
                text = 'По данным запросам товары на WB отсутствуют.'
                os.remove(path_to_excel)
            await state.finish()
            markup = markups.another_seo_building_markup() 
        return dict(text=text, markup=markup)

    async def instruction_bar(self):
        markup = markups.back_to_main_menu_markup()
        text = f"{FAQ} {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
        return dict(text=text, markup=markup)
