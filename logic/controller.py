from db.db_connector import Database
from logic.notification_service import Notification_Service
from .inline_buttons_process_callback import InlineCallback
from . import states
from . import wildberries as wb
from . import mpstats
from . import utils
from . import markups
from const.phrases import *
from const.const import *
from aiogram.utils.markdown import hlink
from aiogram import types
from math import ceil
from datetime import date
import json
import re
import os
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
            text = f"<b>Приветствую, {name}!</b>\n\nЭто наш бот🤖 для улучшения карточки твоего товара на WB.\n" \
                "Для доступа к функционалу бота, пожалуйста, подпишись на канал {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
            markup = markups.not_subscribed_markup()
            return dict(text=text, markup=markup)

        user = self.db.get_user(message.from_user.id)
        if user:
            text = '<b>Это главное меню</b>\n\nВыбери нужную функцию или сначала загляни в подсказку ' \
                   '<b>"Как пользоваться ботом"</b>'
            is_admin = self.db.check_for_admin(message.from_user.id)
            if is_admin:  # check for existing in db?
                markup = markups.admin_start_menu_markup()
            else:
                markup = markups.start_menu_markup()
        else:
            text = 'Для начала мы хотим узнать немного о тебе.\n' + \
                '<b>Пожалуйста, введи своё имя</b>.'
            markup = None
            await state.set_state(states.User.name)
        return dict(text=text, markup=markup)

    # ________________________admin_part_______________________________
    async def get_number_of_users(self):
        markup = markups.admin_start_menu_markup()
        number_of_users = self.db.get_number_of_users()
        text = f'В нашем боте зарегистриован {number_of_users} пользователь.'
        return dict(text=text, markup=markup)

    async def get_data_from_db(self, message):
        markup = markups.admin_start_menu_markup()
        file_name = self.db.get_data_from_db()
        await message.answer_document(document=types.InputFile(file_name))
        os.remove(file_name)
        text = 'Это актуальная выгрузка из всей БД.'
        return dict(text=text, markup=markup)

    async def pre_step_for_add_admin(self, state):
        text = 'Введи tg_id пользователя, которому вы хотите дать права админа.\n' \
                'Пользователь может узнать свой tg_id с помощью бота @getmyid_bot . ' \
                'Достаточно лишь начать с ним общение. ' \
                'Или можно найти эту информацию в выгрузке из БД.'
        markup = markups.back_to_main_menu_markup()
        await state.set_state(states.Admin.tg_id_to_add)
        return dict(text=text, markup=markup)

    async def add_admin(self, message, state):
        if message.text == 'Назад в главное меню':
            await state.finish()
            text = "<b>Это главное меню</b>"
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
        text = 'Введи tg_id пользователя, которого вы хотите лишить прав админа.\n' \
            'Пользователь может узнать свой tg_id с помощью бота @getmyid_bot . ' \
            'Достаточно лишь начать с ним общение.' \
            'Или можно найти эту информацию в выгрузке из БД.'
        markup = markups.back_to_main_menu_markup()
        await state.set_state(states.Admin.tg_id_to_delete)
        return dict(text=text, markup=markup)

    async def delete_admin(self, message, state):
        if message.text == 'Назад в главное меню':
            await state.finish()
            text = "<b>Это главное меню</b>"
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
                text = 'Пожалуйста, введи id в числовом формате.'
        markup = markups.admin_start_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def pre_step_for_mailing_to_clients(self, state):
        text = 'Введи сообщение, которое будет отправлено ВСЕМ пользователям, зарегистрированным в боте ' \
               '(но не заблокировавшим его). В сообщении можно использовать смайлы и <b>средства HTML</b>.'
        markup = markups.back_to_main_menu_markup()
        await state.set_state(states.Admin.message_to_clients)
        return dict(text=text, markup=markup)

    async def confirmation_mailing_to_clients(self, message, state):
        async with state.proxy() as data:
            data['message_to_clients'] = message.text
        text = f'Пример сообщения ниже. Отправляем?\n\n{message.text}'
        markup = markups.confirmation_mailing_markup()
        return dict(text=text, markup=markup)

    async def mailing_to_clients(self, state):
        tg_id_list = self.db.get_all_users_list()
        async with state.proxy() as data:
            for tg_id in tg_id_list:
                try:
                    await self.bot.send_message(tg_id, data['message_to_clients'], parse_mode='HTML')
                    #print(f'{tg_id} успешно.')
                except BotBlocked:
                    pass
                    #print(f'{tg_id} не подписан на канал.')
        text = 'Сообщение отправлено успешно!'
        markup = markups.admin_start_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    # ____________________end_of_admin_part____________________________

    async def message_name_state(self, message, state):
        name_pattern = r'[ёЁА-Яа-я- A-za-z]+'
        if re.fullmatch(name_pattern, message.text):
            async with state.proxy() as data:
                data['name'] = message.text
            text = '<b>Пожалуйста, введи свой e-mail</b>.'
            markup = markups.back_to_name_markup()
            await state.set_state(states.User.email)
        else:
            text = 'Не похоже на твоё имя. Введи что-то более корректное (только буквы и дефис).'
            markup = None
        return dict(text=text, markup=markup)

    async def message_email_state(self, message, state):
        email_pattern = r'([A-Za-z0-9]+[\.\-\_])*[A-Za-z0-9]+@[A-Za-z0-9]+[A-Za-z0-9-\+]*[A-Za-z0-9]+(\.[A-Z|a-z]{2,})+'
        if re.fullmatch(email_pattern, message.text):
            async with state.proxy() as data:
                data['email'] = message.text
            text = '<b>Пожалуйста, введи свой номер телефона</b>.'
            markup = markups.back_to_email_markup()
            await state.set_state(states.User.phone_number)
        elif message.text == 'Назад к вводу имени':
            text = '<b>Пожалуйста, введи своё имя</b>.'
            markup = None
            await state.set_state(states.User.name)
        else:
            text = 'Не похоже на email. Введи что-то более корректное (только английские буквы, цифры и спецсимволы).'
            markup = markups.back_to_name_markup()
        return dict(text=text, markup=markup)

    async def message_phone_number_state(self, message, state):
        phone_pattern = re.compile(r'[0-9 \+\-\(\)]{7,}')
        if re.fullmatch(phone_pattern, message.text):
            async with state.proxy() as data:
                data['phone_number'] = message.text
                self.db.add_user(message.from_user.id,
                                 message.from_user.username,
                                 data['name'],
                                 data['email'],
                                 data['phone_number'])
            await state.finish()
            text = '<b>Спасибо за информацию!</b>\nТеперь тебе доступны все функции нашего бота.'
            is_admin = self.db.check_for_admin(message.from_user.id)
            if is_admin:
                markup = markups.admin_start_menu_markup()
            else:
                markup = markups.start_menu_markup()
        elif message.text == 'Назад к вводу почты':
            text = '<b>Пожалуйста, введи свой e-mail</b>.'
            markup = markups.back_to_name_markup()
            await state.set_state(states.User.email)
        else:
            text = 'Не похоже на номер телефона. Введи что-то более корректное (только цифры, плюс, минус или скобки).'
            markup = markups.back_to_email_markup()
        return dict(text=text, markup=markup)

    async def search_query(self, state):
        markup = markups.back_to_main_menu_markup()
        text = '<b>Пожалуйста, введи один поисковой запрос</b> 🔎\n\nНаш робот выдаст список вариантов, как его можно "уточнить".\n' \
               'Подобрав наиболее точные поисковые запросы (лучше несколько), можешь собрать по ним SEO - набор слов, ' \
               'которые обязательно надо использовать в карточке своего товара.'
        await state.set_state(states.NameGroup.query)
        return dict(text=text, markup=markup)

    async def giving_hints(self, message, state):
        if message.text == 'Сбор SEO ядра':
            markup = markups.back_to_main_menu_markup()
            text = '<b>Пожалуйста, отправь мне все поисковые запросы для твоего товара</b>.\n\n' \
                   'Я соберу SEO у 100 популярнейших карточек на WB по этим запросам.\n' \
                   '<b>Каждый запрос с новой строки.</b>'
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
            text = 'Ты ввел конечный поисковый запрос. Его уже никак не улучшить.\n' \
                   '<b>Может использовать его для сбора SEO?</b>'
        else:
            text = 'По твоему запросу продолжений на Wildberries не найдено.\n<b>Попробуй другой запрос</b>.'
        markup = markups.another_search_query_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def building_seo_core(self, state):
        markup = markups.back_to_main_menu_markup()
        text = '<b>Пожалуйста, отправь мне все поисковые запросы для твоего товара</b>.\n\n' \
                'Я соберу SEO у 100 популярнейших карточек на WB по этим запросам.\n' \
                '<b>Каждый запрос с новой строки.</b>'
        await state.set_state(states.NameGroup.SEO_queries)
        return dict(text=text, markup=markup)

    async def waiting_seo_result(self, message, state):
        async with state.proxy() as data:
            data['SEO_queries'] = message.text
        text = '<b>Подготавливаем excel-файл..</b>\nЭто может занять до 1 минуты (в зависимости от количества запросов).'
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
                text = '<b>SEO подготовлено!</b>'
            else:
                text = '<b>По данным запросам товары на WB отсутствуют.</b>\nПопробуешь другие?'
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
            text = '🔎<b>Поиск запущен..</b>\nРезультат скоро появится.'
            markup = None
            is_valid_query = True
        else:
            text = '<b>Проверьте корректность введенного запроса.</b>\n'\
                   'Запрос должен состоять из артикула (8 цифр) и поискового запроса, разделенных пробелом.'
            markup = markups.another_card_position_search_markup()
            is_valid_query = False
        return dict(text=text, markup=markup, is_valid_query=is_valid_query)

    async def article_search(self, message, state):
        async with state.proxy() as data:
            art_number = int(data['range_search'][0])
            query = data['range_search'][1]
            position = wb.search_for_article(art_number, query)
            if position:
                text = f"Артикул {art_number} по запросу {query} найден!\n\n" \
                    f"<b>Страница: {position[0]}\nПозиция: {position[1]}</b>"
                user = self.db.get_user(tg_id=message.from_user.id)
                if user:
                    self.db.add_search_position_query(
                        search_position_query=message.text,
                        tg_id=message.from_user.id)
            else:
                text = '<b>Товара по данному запросу не обнаружено.</b>\nПопробуешь другой?'
        markup = markups.another_card_position_search_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def category_selection(self, state):
        parent = "0"
        categories = json.load(open("static/cats/" + parent + ".json"))
        text = phrase_for_categories_inline_keyboard(data=dict(category="",
                                                               current_page=1,
                                                               total_page=ceil(len(categories)/10)))
        markup = markups.inline_categories_markup(
            categories=[dict(id=key, name=value.split('/')[-1]) for key, value in categories.items()][:10],
            cat_id=parent,
            next_page=2,
            back_to=False,
            select=False)
        return dict(text=text, markup=markup)

    # ________________________логика по выдаче графиков________________________
    # выбираем category для выдачи графика -> предлагаем выбрать view
    async def callback_graph_category_selection(self, query, state):
        category = await self.inline_buttons_callback.process_callback(query)
        if not category:
            return None
        async with state.proxy() as state:
            state['category'] = category
        text = 'Выберите VIEW'
        markup = markups.graph_view_selection_markup()
        return dict(text=text, markup=markup)

    # выбрали view -> предлагаем выбрать value
    async def graph_view_selection(self, message, state):
        async with state.proxy() as state:
            state['view'] = message.text
        text = 'Выберите VALUE'
        markup = markups.graph_value_selection_markup()
        return dict(text=text, markup=markup)

    # выбрали value -> предлагаем ввести date_1
    async def graph_value_selection(self, message, state):
        async with state.proxy() as state:
            state['value'] = message.text
        text = 'Введите дату начала периода в формате гггг-мм-дд'
        markup = markups.back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    # ввели date_1 -> предлагаем ввести date_2
    async def graph_date_1_selection(self, message, state):
        async with state.proxy() as state:
            state['date_1'] = date(*map(int, message.text.split('-')))
        text = 'Введите дату окончания периода в формате гггг-мм-дд'
        markup = markups.back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    # выбрали date_2 -> выдаем график
    async def graph_date_2_selection(self, message, state):
        async with state.proxy() as state:
            state['date_2'] = date(*map(int, message.text.split('-')))
        await message.answer(text='Подготовливаем график...',
                             reply_markup=markups.back_to_main_menu_markup())
        trend_data = mpstats.get_trends_data(state['category'], state['view'])
        path_to_graph = utils.make_graph(value=state['value'],
                                         data=trend_data,
                                         date_1=state['date_1'],
                                         date_2=state['date_2'],
                                         category=state['category'])
        if path_to_graph:
            await self.bot.send_document(chat_id=message.from_user.id,
                                         document=types.InputFile(path_to_graph))
            os.remove(path_to_graph)
            text = 'График по вашему запросу готов!'
        else:
            text = 'Ошибка на стороне сервера, пока что мы не можем этого исправить 😔\n\n' \
                'Попробуй повторить запрос или изменить категорию товара.'
        markup = markups.another_trend_graph_markup()
        return dict(text=text, markup=markup)
    # __________________окончание логики по выдаче графиков__________________

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
                text = '<b>Пожалуйста, ценовая сегментация готова.</b>'
            else:
                text = 'Ошибка на стороне сервера, пока что мы не можем этого исправить 😔\n\n' \
                       'Попробуй повторить запрос или изменить категорию товара.'
            markup = markups.another_price_segmentation_markup()
            return dict(text=text, markup=markup)
    
    async def price_segmentation(self, message, query):
        if query.message.text == 'Назад в главное меню':
            name = query.message.from_user.first_name
            text = "<b>Это главное меню</b>"
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
                text = '<b>Пожалуйста, ценовая сегментация готова.</b>'
                await message.answer_document(document=types.InputFile(path_to_excel))
                os.remove(path_to_excel)
            else:
                text = 'Ты ввел невалидную категорию. Пожалуйста, используй клавиатуру.'
            markup = markups.another_price_segmentation_markup()
        return dict(text=text, markup=markup)

    async def instruction_bar(self):
        markup = markups.back_to_main_menu_markup()
        text = f"{FAQ} {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
        return dict(text=text, markup=markup)
