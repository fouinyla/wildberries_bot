from db.db_connector import Database
from . import markups
from logic.notification_service import Notification_Service
from . import states
from . import wildberries as wb
from . import mpstats
from const.phrases import *
from const.const import *
import re
import os
from aiogram.utils.markdown import hlink
from aiogram import types
from .inline_buttons_process_callback import InlineCallback
import json
from math import ceil
from const import phrases
from . import utils
from datetime import date
from aiogram.utils.exceptions import BotBlocked


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.notification = Notification_Service(bot=self.bot)
        self.inline_buttons_callback = InlineCallback(bot=self.bot)

    async def subscribed(self, user_id: int) -> bool:
        """
        Checks if user is subscribed to the customer's channel.
        """
        status = await self.bot.get_chat_member(chat_id=CUSTOMER_CHANNEL_ID,
                                                user_id=user_id)
        return status['status'] != 'left'

    async def command_start(self, message, state):
        await state.finish()

        if not await self.subscribed(message.from_user.id):
            name = message.from_user.first_name
            text = f"Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.\n" \
                "Для доступа к функционалу бота подпишитесь на канал {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
            markup = markups.not_subscribed_markup()
            return dict(text=text, markup=markup)

        user = self.db.get_user(message.from_user.id)
        if user:
            is_admin = self.db.check_for_admin(message.from_user.id)
            text = "Вы в главном меню. Пожалуйста, выберите необходимую функцию."
            if is_admin:  # check for existing in db?
                markup = markups.admin_start_menu_markup()
            else:
                markup = markups.start_menu_markup()
        else:
            text = 'Для начала мы хотим узнать немного о тебе.\n' + \
                'Пожалуйста, введи своё имя.'
            markup = None
            await state.set_state(states.User.name)
        return dict(text=text, markup=markup)

    # ________________________admin_part_______________________________
    async def get_number_of_users(self):
        markup = markups.admin_start_menu_markup()
        number_of_users = self.db.get_number_of_users()
        text = f'Сейчас в БД {number_of_users} user.'
        return dict(text=text, markup=markup)

    async def get_data_from_db(self, message):
        markup = markups.admin_start_menu_markup()
        file_name = self.db.get_data_from_db()
        await message.answer_document(document=types.InputFile(file_name))
        os.remove(file_name)
        text = 'Это актуальная выгрузка из БД.'
        return dict(text=text, markup=markup)

    async def pre_step_for_add_admin(self, state):
        text = 'Введите tg_id пользователя, которому вы хотите дать права админа.\n' + \
            'Пользователь может узнать свой tg_id с помощью бота @getmyid_bot. ' + \
            'Достаточно лишь начать с ним общение.'
        markup = markups.back_to_main_menu_markup()
        await state.set_state(states.Admin.tg_id_to_add)
        return dict(text=text, markup=markup)

    async def add_admin(self, message, state):
        if message.text == 'Назад в главное меню':
            await state.finish()
            text = "Вы в главном меню. Пожалуйста, выберите необходимую функцию."
        else:
            if message.text.isdigit():
                new_admin_tg_id = int(message.text)
                new_admin = self.db.get_user(new_admin_tg_id)
                if new_admin:
                    self.db.add_admin_to_user(new_admin_tg_id)
                    text = f"Пользователю {new_admin['tg_nickname']} добавлены права админа."
                else:
                    text = f'Такого пользователя нет в БД.\nСначала ему необходимо зарегистрироваться в боте.'
            else:
                text = 'Пожалуйста, введите id в числовом формате.'
        markup = markups.admin_start_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def pre_step_for_delete_admin(self, state):
        text = 'Введите tg_id пользователя, которому вы хотите дать права админа.\n' + \
            'Пользователь может узнать свой tg_id с помощью бота @getmyid_bot. ' + \
            'Достаточно лишь начать с ним общение.'
        markup = markups.back_to_main_menu_markup()
        await state.set_state(states.Admin.tg_id_to_delete)
        return dict(text=text, markup=markup)

    async def delete_admin(self, message, state):
        if message.text == 'Назад в главное меню':
            await state.finish()
            text = "Вы в главном меню. Пожалуйста, выберите необходимую функцию."
        else:
            if message.text.isdigit():
                del_admin_tg_id = int(message.text)
                del_admin = self.db.get_user(del_admin_tg_id)
                if del_admin:
                    self.db.delete_admin_to_user(del_admin_tg_id)
                    text = f"У пользователя {del_admin['tg_nickname']} удалены права админа."
                else:
                    text = f'Такого пользователя нет в БД.\nА значит и админки у него нет.'
            else:
                text = 'Пожалуйста, введите id в числовом формате.'
        markup = markups.admin_start_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def pre_step_for_mailing_to_clients(self, state):
        text = 'Введите сообщение, которое будет отправлено на ВСЕХ пользователей, зарегистрированных в боте.'
        markup = markups.back_to_main_menu_markup()
        await state.set_state(states.Admin.message_to_clients)
        return dict(text=text, markup=markup)

    async def confirmation_mailing_to_clients(self, message, state):
        async with state.proxy() as data:
            data['message_to_clients'] = message.text
        text = f'Прошу подтверждения, все ли корректно:\n\n{message.text}'
        markup = markups.confirmation_mailing_markup()
        return dict(text=text, markup=markup)

    async def mailing_to_clients(self, state):
        tg_id_list = self.db.get_all_users_list()
        async with state.proxy() as data:
            for tg_id in tg_id_list:
                try:
                    await self.bot.send_message(tg_id, data['message_to_clients'], parse_mode='HTML')
                    print(f'{tg_id} успешно.')
                except BotBlocked:
                    print(f'{tg_id} не подписан на канал.')
        text = 'Сообщение отправлено.'
        markup = markups.admin_start_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    # ____________________end_of_admin_part____________________________

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
        email_pattern = r'([A-Za-z0-9]+[\.\-\_])*[A-Za-z0-9]+@[A-Za-z0-9]+[A-Za-z0-9-\+]*[A-Za-z0-9]+(\.[A-Z|a-z]{2,})+'
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
            text = 'Спасибо за информацию! Теперь тебе доступны все функции нашего бота.'
            is_admin = self.db.check_for_admin(message.from_user.id)
            if is_admin:
                markup = markups.admin_start_menu_markup()
            else:
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
            self.db.add_search_query(search_query=message.text,
                                     user_id=user['id'])
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
            path_to_excel, flag_all_empty_queries = mpstats.get_seo(data['SEO_queries'])
            if not flag_all_empty_queries:
                await message.answer_document(document=types.InputFile(path_to_excel))
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

    async def position_search(self, state):
        markup = markups.back_to_main_menu_markup()
        text = CARD_POSITION_TEXT
        await state.set_state(states.NameGroup.range_search)
        return dict(text=text, markup=markup)

    async def waiting_for_article_search(self, message, state):
        range_search_pattern = r'[0-9]{8}\s.+'
        if re.fullmatch(range_search_pattern, message.text):
            async with state.proxy() as data:
                data['range_search'] = message.text.split(' ', maxsplit=1)
            text = '🔎<b>Поиск запущен..</b> Результат скоро появится.'
            markup = None
            is_valid_query = True
        else:
            text = 'Проверьте корректность введенного запроса.\n'\
                   'Запрос должен состоять из артикула и поискового запроса, разделенных пробелом.'
            markup = markups.another_card_position_search_markup()
            is_valid_query = False
        return dict(text=text, markup=markup, is_valid_query=is_valid_query)

    async def article_search(self, message, state):
        async with state.proxy() as data:
            art_number = int(data['range_search'][0])
            query = data['range_search'][1]
            position = wb.search_for_article(art_number, query)
            if position:
                text = f"Артикул {art_number} по запросу " \
                    f"{query} найден:\n\n" \
                    f"Страница {position[0]}\nПозиция {position[1]}"
                user = self.db.get_user(tg_id=message.from_user.id)
                if user:
                    self.db.add_search_position_query(
                        search_position_query=message.text,
                        tg_id=message.from_user.id
                    )
            else:
                text = 'Товара по данному запросу не обнаружено.'
        markup = markups.another_card_position_search_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def category_selection(self, state):
        parent = "0"
        categories = json.load(open("static/cats/" + parent + ".json"))
        text = phrases.phrase_for_categories_inline_keyboard(
            data=dict(category="",
                      current_page=1,
                      total_page=ceil(len(categories)/10)))
        markup = markups.inline_categories_markup(
            categories=[dict(id=key, name=value.split('/')[-1]) for key, value in categories.items()][:10],
            cat_id=parent,
            next_page=2,
            back_to=False,
            select=False)
        return dict(text=text, markup=markup)

    async def callback_trend_graph(self, query):
        path = await self.inline_buttons_callback.process_callback(query)
        if not path:
            return None
        trend_data = mpstats.get_trends_data(path, 'itemsInCategory')  # !!!!!!! ПРЕДОСТАВИТЬ ВЫБОР VIEW
        path_to_graph = utils.make_graph(value='Число продаж',         # !!!!!!! ПРЕДОСТАВИТЬ ВЫБОР ПАРАМЕТРОВ
                                         data=trend_data,
                                         date_1=date(2022, 1, 1),
                                         date_2=date(2022, 4, 1),
                                         header=path)
        if path_to_graph:
            user = self.db.get_user(tg_id=query.from_user.id)
            if user:
                self.db.add_price_query(query_for_price=path,
                                        tg_id=query.from_user.id)

            await self.bot.send_document(chat_id=query.from_user.id,
                                         document=types.InputFile(path_to_graph))
            os.remove(path_to_graph)
            text = 'График по вашему запросу готов!'
        else:
            text = 'Ошибка на стороне сервера. Попробуйте повторить запрос или изменить категорию товара.'
        markup = markups.another_price_segmentation_markup()
        return dict(text=text, markup=markup)

    async def callback_price_segmentation(self, query):
        path = await self.inline_buttons_callback.process_callback(query)
        if path:
            path_to_excel = mpstats.get_price_segmentation(path)
            if path_to_excel:
                user = self.db.get_user(tg_id=query.from_user.id)
                if user:
                    self.db.add_price_query(query_for_price=path,
                                            tg_id=query.from_user.id)
                
                await self.bot.send_document(chat_id=query.from_user.id, document=types.InputFile(path_to_excel))
                os.remove(path_to_excel)
                text = 'Пожалуйста, ценовая сегментация в таблице.'
            else:
                text = 'Ошибка на стороне сервера. Попробуйте повторить запрос или изменить категорию товара.'
            markup = markups.another_price_segmentation_markup()
            return dict(text=text, markup=markup)
    
    async def price_segmentation(self, message, query):
        if query.message.text == 'Назад в главное меню':
            name = query.message.from_user.first_name
            text = "Вы в главном меню. Пожалуйста, выберите необходимую функцию."
            is_admin = self.db.check_for_admin(query.message.from_user.id)
            if is_admin:
                markup = markups.admin_start_menu_markup()
            else:
                markup = markups.start_menu_markup()
        else:
            path_to_excel = await self.inline_buttons_callback.process_callback(query.message.text)
            if path_to_excel:
                user = self.db.get_user(tg_id=message.from_user.id)
                if user:
                    self.db.add_price_query(query_for_price=message.text,
                                            tg_id=message.from_user.id)
                text = 'Пожалуйста, ценовая сегментация для данной категории в таблице.'
                await message.answer_document(document=types.InputFile(path_to_excel))
                os.remove(path_to_excel)
            else:
                text = 'Вы ввели невалидную категорию.'
            markup = markups.another_price_segmentation_markup()
        return dict(text=text, markup=markup)

    async def instruction_bar(self):
        markup = markups.back_to_main_menu_markup()
        text = f"{FAQ} {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
        return dict(text=text, markup=markup)
