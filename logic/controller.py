from db.db_connector import Database
from logic.notification_service import Notification_Service
from .inline_buttons_process_callback import InlineCallback
from . import states
from . import wildberries as wb
from . import mpstats
from .utils import *
from .markups import *
from const.phrases import *
from const.const import *
from . import memory
from aiogram.utils.markdown import hlink
from aiogram.utils.exceptions import BotBlocked
from aiogram.types import InputFile, ReplyKeyboardRemove
from math import ceil
from datetime import date
import json
import re
import os
from .web import error


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.notification = Notification_Service(bot=self.bot)
        self.inline_buttons_callback = InlineCallback(bot=self.bot)
        self.load_categories()
        self.load_admins()

    def load_categories(self):
        for f in os.listdir("static/cats"):
            with open("static/cats/" + f, mode="r") as json_file:
                memory.categories[f.split(".json")[0]] = json_file.read()

    def load_admins(self):
        memory.admins = self.db.get_admins()

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
                f"Для доступа к функционалу бота, пожалуйста, подпишись на канал {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
            markup = not_subscribed_markup()
            return dict(text=text, markup=markup)

        user = self.db.get_user(message.from_user.id)
        if user:
            text = '<b>Это главное меню</b>\n\nВыберите нужную функцию или сначала загляните в подсказку ' \
                   '<b>"Как пользоваться ботом"</b>'
            if message.from_user.id in memory.admins:
                markup = admin_start_menu_markup()
            else:
                markup = start_menu_markup()
        else:
            text = 'Для начала мы хотим узнать немного о вас.\n' + \
                '<b>Пожалуйста, введите ваше имя</b>.'
            markup = None
            await state.set_state(states.User.name)
        return dict(text=text, markup=markup)

    # _________________________Функции админа________________________________
    async def admin_menu(self, state):
        await state.finish()
        markup = admin_menu_markup()
        text = '<b>Это меню админа</b>'
        return dict(text=text, markup=markup)

    async def get_number_of_users(self):
        markup = admin_menu_markup()
        number_of_users = self.db.get_number_of_users()
        last_number = number_of_users % 10
        ending = '' if last_number == 1 else 'о'
        text = f'В нашем боте зарегистрирован{ending} {number_of_users} пользовател{ENDINGS_FOR_WORD_USER[last_number]}.'
        return dict(text=text, markup=markup)

    async def get_data_from_db(self, message):
        markup = admin_menu_markup()
        file_name = self.db.get_data_from_db()
        await message.answer_document(document=InputFile(file_name))
        os.remove(file_name)
        text = 'Это актуальная выгрузка из всей БД.'
        return dict(text=text, markup=markup)

    async def pre_step_for_add_admin(self, state):
        text = 'Введите tg_id пользователя, которому вы хотите дать права админа.\n' \
            'Пользователь может узнать свой tg_id с помощью бота @getmyid_bot . ' \
            'Достаточно лишь начать с ним общение. ' \
            'Или можно найти эту информацию в выгрузке из БД.'
        markup = back_to_admin_menu_markup()
        await state.set_state(states.Admin.tg_id_to_add)
        return dict(text=text, markup=markup)

    async def add_admin(self, message, state):
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
        markup = admin_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def pre_step_for_delete_admin(self, state):
        text = 'Введите tg_id пользователя, которого вы хотите лишить прав админа.\n' \
            'Пользователь может узнать свой tg_id с помощью бота @getmyid_bot . ' \
            'Достаточно лишь начать с ним общение.' \
            'Или можно найти эту информацию в выгрузке из БД.'
        markup = back_to_admin_menu_markup()
        await state.set_state(states.Admin.tg_id_to_delete)
        return dict(text=text, markup=markup)

    async def delete_admin(self, message, state):
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
        markup = admin_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def pre_step_for_mailing_to_clients(self, state):
        text = 'Введите сообщение, которое будет отправлено ВСЕМ пользователям, зарегистрированным в боте ' \
               '(но не заблокировавшим его). В сообщении можно использовать смайлы и <b>средства HTML</b>.'
        markup = back_to_admin_menu_markup()
        await state.set_state(states.Admin.message_to_clients)
        return dict(text=text, markup=markup)

    async def confirmation_mailing_to_clients(self, message, state):
        async with state.proxy() as data:
            data['message_to_clients'] = message.text
        text = f'Пример сообщения ниже. Отправляем?\n\n{message.text}'
        markup = confirmation_mailing_markup()
        return dict(text=text, markup=markup)

    async def mailing_to_clients(self, state):
        tg_id_list = self.db.get_all_users_list()
        async with state.proxy() as data:
            for tg_id in tg_id_list:
                try:
                    await self.bot.send_message(tg_id, data['message_to_clients'], parse_mode='HTML')
                except BotBlocked:
                    pass
        text = 'Сообщение отправлено успешно!'
        markup = admin_menu_markup()
        await state.finish()
        return dict(text=text, markup=markup)
    # _____________________Окончание функций админа____________________________

    # ________________________Сбор данных пользователя________________________
    async def get_name(self, message, state):
        name_pattern = r'[ёЁА-Яа-я- A-za-z]+'
        if re.fullmatch(name_pattern, message.text):
            async with state.proxy() as data:
                data['name'] = message.text
            text = '<b>Пожалуйста, введите ваш e-mail</b>.'
            markup = back_to_name_markup()
            await state.set_state(states.User.email)
        else:
            text = 'Не похоже на ваше имя. Введите что-то более корректное (только буквы и дефис).'
            markup = None
        return dict(text=text, markup=markup)

    async def get_email(self, message, state):
        email_pattern = r'([A-Za-z0-9]+[\.\-\_])*[A-Za-z0-9]+@[A-Za-z0-9]+[A-Za-z0-9-\+]*[A-Za-z0-9]+(\.[A-Z|a-z]{2,})+'
        if re.fullmatch(email_pattern, message.text):
            async with state.proxy() as data:
                data['email'] = message.text
            text = "<b>Для регистрации в нашем боте необходим номер телефона</b>.\nПожалуйста, воспользуйтесь кнопкой 'Отправить номер телефона'"
            markup = back_to_email_markup()
            await state.set_state(states.User.phone_number)
        elif message.text == 'Назад к вводу имени':
            text = '<b>Пожалуйста, введите ваше имя</b>.'
            markup = ReplyKeyboardRemove()
            await state.set_state(states.User.name)
        else:
            text = 'Не похоже на email. Введите что-то более корректное (только английские буквы, цифры и спецсимволы).'
            markup = back_to_name_markup()
        return dict(text=text, markup=markup)

    async def get_phone_number(self, message, state):
        if message.text == 'Назад к вводу почты':
            text = '<b>Пожалуйста, введите ваш e-mail</b>.'
            markup = back_to_name_markup()
            await state.set_state(states.User.email)
        elif message.contact:
            async with state.proxy() as data:
                self.db.add_user(
                    tg_id=message.from_user.id,
                    tg_nickname=message.from_user.username,
                    name=data['name'],
                    email=data['email'],
                    phone_number=message.contact.phone_number.strip('+'))
            await state.finish()
            text = '<b>Спасибо за информацию!</b>\nТеперь вам доступны все функции нашего бота.'
            markup = start_menu_markup()
        else:
            text = "<b>Для регистрации в нашем боте необходим номер телефона</b>.\nПожалуйста, воспользуйтесь кнопкой 'Отправить номер телефона'"
            markup = back_to_email_markup()
        return dict(text=text, markup=markup)

    # __________________Окончание сбора данных пользователя__________________

    async def search_query(self, state):
        markup = back_to_main_menu_markup()
        text = '<b>Пожалуйста, введите один поисковой запрос</b> 🔎\n\nНаш робот выдаст список вариантов, как его можно "уточнить".\n' \
               'Подобрав наиболее точные поисковые запросы (лучше несколько), можете собрать по ним SEO - набор слов, ' \
               'которые обязательно надо использовать в карточке вашего товара.'
        await state.set_state(states.NameGroup.query)
        return dict(text=text, markup=markup)

    async def giving_hints(self, message, state):
        query = message.text
        user = self.db.get_user(tg_id=message.from_user.id)
        if user:
            self.db.add_search_query(search_query=query, user_id=user['id'])
        hints = await wb.get_hints(query)
        # product_exists = await wb.product_exists(query)
        product_exists = True
        if error in (hints, product_exists):
            text = phrase_service_unavailable()
        elif hints:
            text = '\n'.join(hints)
        elif hints == [] or (hints is None and product_exists):
            text = 'Вы ввели конечный поисковый запрос. Его уже никак не улучшить.\n' \
                   '<b>Может использовать его для сбора SEO?</b>'
        else:
            text = 'По вашему запросу продолжений на Wildberries не найдено.\n<b>Попробуйте другой запрос</b>.'
        markup = another_search_query_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def building_seo_core(self, state):
        markup = back_to_main_menu_markup()
        text = '<b>Пожалуйста, отправьте мне все поисковые запросы для вашего товара</b>.\n\n' \
            'Я соберу SEO у 100 популярнейших карточек на WB по этим запросам.\n' \
            '<b>Каждый запрос с новой строки.</b>'
        await state.set_state(states.NameGroup.SEO_queries)
        return dict(text=text, markup=markup)

    async def waiting_seo_result(self, message, state):
        async with state.proxy() as data:
            data['SEO_queries'] = message.text
        text = '<b>Подготавливаем excel-файл..</b>\nЭто может занять до 1 минуты (в зависимости от количества запросов).'
        markup = back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    async def building_seo_result(self, message, state):
        async with state.proxy() as data:
            seo_queries = data['SEO_queries']

        seo_data = await mpstats.get_seo(seo_queries)

        if seo_data is error:
            text = phrase_service_unavailable()
            markup = another_seo_building_markup()
            await state.finish()
            return dict(text=text, markup=markup)

        path_to_excel, flag_all_empty_queries = seo_data

        if not flag_all_empty_queries:
            await message.answer_document(document=InputFile(path_to_excel))
            user = self.db.get_user(tg_id=message.from_user.id)
            if user:
                query_for_seo = str(message.text).replace('\n', '; ')
                self.db.add_SEO_query(query_for_SEO=query_for_seo,
                                      tg_id=message.from_user.id)
            text = '<b>SEO подготовлено!</b>'
        else:
            text = '<b>По данным запросам товары на WB отсутствуют.</b>\nПопробуете другие?'

        os.remove(path_to_excel)
        await state.finish()
        markup = another_seo_building_markup()
        return dict(text=text, markup=markup)

    async def position_search(self, state):
        markup = back_to_main_menu_markup()
        text = CARD_POSITION_TEXT
        await state.set_state(states.NameGroup.range_search)
        return dict(text=text, markup=markup)

    async def waiting_for_article_search(self, message, state):
        range_search_pattern = r'[0-9]{8,9}\s.+'
        if re.fullmatch(range_search_pattern, message.text):
            async with state.proxy() as data:
                data['range_search'] = message.text.split(' ', maxsplit=1)
            text = '🔎<b>Поиск запущен..</b>\nРезультат скоро появится.'
            markup = None
            is_valid_query = True
        else:
            text = '<b>Проверьте корректность введенного запроса.</b>\n'\
                   'Запрос должен состоять из артикула (8 или 9 цифр) и поискового запроса, разделенных пробелом.'
            markup = another_card_position_search_markup()
            is_valid_query = False
        return dict(text=text, markup=markup, is_valid_query=is_valid_query)

    async def article_search(self, message, state):
        async with state.proxy() as data:
            art_number = int(data['range_search'][0])
            query = data['range_search'][1]
        position = await wb.search_for_article(art_number, query)
        if position is error:
            text = phrase_service_unavailable()
        elif position:
            text = f"Артикул {art_number} по запросу {query} найден!\n\n" \
                   f"<b>Страница: {position[0]}\nПозиция: {position[1]}</b>"
            user = self.db.get_user(tg_id=message.from_user.id)
            if user:
                self.db.add_search_position_query(
                    search_position_query=message.text,
                    tg_id=message.from_user.id)
        else:
            text = '<b>Товара по данному запросу не обнаружено.</b>\nПопробуете другой?'
        markup = another_card_position_search_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def category_selection(self, state):
        parent = '0'
        categories = json.load(open(f'static/cats/{parent}.json'))
        text = phrase_for_categories_inline_keyboard(data=dict(category='',
                                                               current_page=1,
                                                               total_page=ceil(len(categories)/INLINE_CATS_COUNT_PER_PAGE)))
        markup = inline_categories_markup(
            categories=[dict(id=key, name=value.split('/')[-1]) for key, value in categories.items()][:INLINE_CATS_COUNT_PER_PAGE],
            cat_id=parent,
            next_page=2,
            back_to=False,
            select=False)
        return dict(text=text, markup=markup)

    # ________________________логика по выдаче графиков________________________
    # выбираем category для выдачи графика -> предлагаем выбрать value
    async def callback_graph_category_selection(self, query, state):
        category = await self.inline_buttons_callback.process_callback(query)
        if not category:
            return False
        async with state.proxy() as state:
            state['category'] = category
        text = 'По какому параметру составить график?'
        markup = graph_value_selection_markup()
        await self.bot.send_message(chat_id=query.from_user.id,
                                    text=text,
                                    reply_markup=markup)
        return True

    # выбрали value -> предлагаем ввести date_1
    async def graph_value_selection(self, message, state):
        if message.text not in MPSTATS_TRENDS:
            text = 'Вы ввели невалидный параметр. Пожалуйста, используйте предложенную клавиатуру.'
            markup = graph_value_selection_markup()
            await message.answer(text=text, reply_markup=markup)
            return False
        async with state.proxy() as proxy:
            proxy['value'] = message.text
            category = proxy['category']
            value = proxy['value']
        text = 'Проверяем наличие статистики...'
        markup = back_to_main_menu_markup()
        await message.answer(text=text, reply_markup=markup)
        graph_data = await mpstats.get_trends_data(category)
        if graph_data is error:
            text = phrase_service_unavailable()
            markup = another_trend_graph_markup()
            await message.answer(text=text, reply_markup=markup)
            await state.finish()
            return False
        if not graph_data:
            text = 'К сожалению, у нас нет статистики по данной категории, выберите другую категорию'
            markup = another_trend_graph_markup()
            await message.answer(text=text, reply_markup=markup)
            return None
        min_date, max_date = get_min_max_week(graph_data, value)
        if min_date is None:
            text = 'К сожалению, по данному параметру у нас нет статистики, выберите другой параметр'
            markup = graph_value_selection_markup()
            await message.answer(text=text, reply_markup=markup)
            return False
        async with proxy as proxy:
            proxy['min_date'] = min_date
            proxy['max_date'] = max_date
            proxy['graph_data'] = graph_data
        text = f'По данной категории у нас собрана статистика с {min_date} по {max_date}\n' \
               f'Введите дату начала периода в формате гггг-мм-дд'
        markup = back_to_main_menu_markup()
        await message.answer(text=text, reply_markup=markup)
        return True

    # ввели date_1 -> предлагаем ввести date_2
    async def graph_date_1_selection(self, message, state):
        async with state.proxy() as proxy:
            min_date = proxy['min_date']
            max_date = proxy['max_date']
        if not validate_trand_graph_date(message.text, min_date, max_date):
            text = f'Вы ввели неверную дату начала периода.\n' \
                   f'Введите дату начала периода в формате гггг-мм-дд с {min_date} по {max_date}'
            markup = back_to_main_menu_markup()
            await message.answer(text=text, reply_markup=markup)
            return False
        async with proxy as proxy:
            proxy['date_1'] = date(*map(int, message.text.split('-')))
        text = 'Введите дату окончания периода в формате гггг-мм-дд'
        markup = back_to_main_menu_markup()
        await message.answer(text=text, reply_markup=markup)
        return True

    # выбрали date_2 -> выдаем график
    async def graph_date_2_selection(self, message, state):
        async with state.proxy() as proxy:
            date_1 = proxy['date_1']
            max_date = proxy['max_date']
        if not validate_trand_graph_date(message.text, date_1, max_date):
            text = f'Вы ввели неверную дату окончания периода.\n' \
                   f'Введите дату окончания периода в формате гггг-мм-дд c {date_1} по {max_date}'
            markup = back_to_main_menu_markup()
            await message.answer(text=text, reply_markup=markup)
            return False
        async with proxy as proxy:
            proxy['date_2'] = date(*map(int, message.text.split('-')))
        text = 'Подготавливаем график...'
        markup = back_to_main_menu_markup()
        await message.answer(text=text, reply_markup=markup)
        path_to_graph = make_trand_graph(category=proxy['category'],
                                         value=proxy['value'],
                                         graph_data=proxy['graph_data'],
                                         date_1=proxy['date_1'],
                                         date_2=proxy['date_2'])
        await self.bot.send_document(chat_id=message.from_user.id,
                                     document=InputFile(path_to_graph))
        os.remove(path_to_graph)
        text = 'График по вашему запросу готов!'
        markup = another_trend_graph_markup()
        await message.answer(text=text, reply_markup=markup)
        return True
    # __________________окончание логики по выдаче графиков__________________

    async def callback_price_segmentation(self, query):
        path = await self.inline_buttons_callback.process_callback(query)
        if not path:
            return None
        path_to_excel = await mpstats.get_price_segmentation(path)
        if path_to_excel is error:
            text = phrase_service_unavailable()
        elif path_to_excel:
            user = self.db.get_user(tg_id=query.from_user.id)
            if user:
                self.db.add_price_query(query_for_price=path,
                                        tg_id=query.from_user.id)
            await self.bot.send_document(chat_id=query.from_user.id,
                                         document=InputFile(path_to_excel))
            os.remove(path_to_excel)
            text = '<b>Пожалуйста, ценовая сегментация готова.</b>'
        else:
            text = 'Ошибка на стороне сервера, пока что мы не можем этого исправить 😔\n\n' \
                   'Попробуй повторить запрос или изменить категорию товара.'
        markup = another_price_segmentation_markup()
        return dict(text=text, markup=markup)

    async def get_article_month_sales(self, state):
        text = 'Пришли ОДИН артикул, по которому будем проверять статистику.\n' \
               'Артикул состоит из 8 или 9 цифр.'
        markup = back_to_main_menu_markup()
        await state.set_state(states.NameGroup.article_for_sales)
        return dict(text=text, markup=markup)

    async def waiting_month_sales(self, message, state):
        article_pattern = r'[0-9]{8,9}'
        if re.fullmatch(article_pattern, message.text):
            async with state.proxy() as proxy:
                proxy['article_for_sales'] = message.text
            text = '📈<b>Строим график..</b>\nРезультат скоро появится.'
            markup = None
            is_valid_article = True
        else:
            text = '<b>Проверь корректность введенного артикула.</b>\n'\
                   'Артикул должен состоять из 8 или 9 цифр.'
            markup = another_month_sales_markup()
            is_valid_article = False
        return dict(text=text, markup=markup, is_valid_article=is_valid_article)

    async def ploting_graph_month_sales(self, message, state):
        async with state.proxy() as proxy:
            article = proxy['article_for_sales']
        graph_data = await mpstats.get_card_data(article)
        if graph_data is error:
            text = phrase_service_unavailable()
        elif graph_data:
            result = plot_month_sales_graph(graph_data, article)
            user = self.db.get_user(tg_id=message.from_user.id)
            if user:
                self.db.add_sales_article(article=article,
                                          tg_id=message.from_user.id)
            await self.bot.send_document(chat_id=message.from_user.id,
                                         document=InputFile(result['image_path']))
            os.remove(result['image_path'])
            text = f"Пожалуйста, график за {result['start_day']} - {result['end_day']} готов.\n" \
                   f"<b>Всего продано товара за месяц: {result['total_sales']}\n" \
                   f"Остаток товара на конец месяца: {result['balance_at_the_end']}</b>"
        else:
            text = '<b>Что-то пошло не так.</b>\n' \
                'Проверь, правильность введенного артикула.\n' \
                'Для некоторых товаров с малым количеством продаж статистика отсутствует.'
        markup = another_month_sales_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    async def get_article_card_queries(self, state):
        text = 'Пришли ОДИН артикул, по которому будем проверять статистику запросов.\n' \
               'Артикул состоит из 8 или 9 цифр.\n' \
               '<b>В статистику гарантированно попадает информация только первой страницы ' \
               'результатов поиска на WB (до 100 позиций).</b>'
        markup = back_to_main_menu_markup()
        await state.set_state(states.NameGroup.article_for_queries)
        return dict(text=text, markup=markup)

    async def waiting_queries_table(self, message, state):
        article_pattern = r'[0-9]{8,9}'
        if re.fullmatch(article_pattern, message.text):
            async with state.proxy() as proxy:
                proxy['article_for_queries'] = message.text
            text = '📏<b>Строим таблицу..</b>\nРезультат скоро появится.'
            markup = None
            is_valid_article = True
        else:
            text = '<b>Проверь корректность введенного артикула.</b>\n'\
                   'Артикул должен состоять из 8 или 9 цифр.'
            markup = another_card_queries_markup()
            is_valid_article = False
        return dict(text=text, markup=markup, is_valid_article=is_valid_article)

    async def creating_queries_table(self, message, state):
        async with state.proxy() as proxy:
            article = proxy['article_for_queries']
        card_data = await mpstats.get_card_data(article)
        if card_data is error:
            text = phrase_service_unavailable()
        elif card_data and isinstance(card_data, dict) and isinstance(card_data['words'], dict):
            result = create_queries_table(card_data, article)
            user = self.db.get_user(tg_id=message.from_user.id)
            if user:
                self.db.add_search_article(article=article,
                                           tg_id=message.from_user.id)
            await self.bot.send_document(chat_id=message.from_user.id,
                                         document=InputFile(result))
            os.remove(result)
            text = f'<b>Пожалуйста, таблица с позициями товара в выдачах по наиболее популярным запросам.</b>\n' \
                'В таблице тире "-" означает, что позиция товара по данному запросу больше 100.'
        else:
            text = '<b>Что-то пошло не так.</b>\n' \
                   'Проверь, правильность введенного артикула.\n' \
                   'Для некоторых товаров с малым количеством продаж статистика отсутствует.'
        markup = another_card_queries_markup()
        await state.finish()
        return dict(text=text, markup=markup)

    # __________________начало логики смены названия карточки__________________
    async def rename_card_start(self, state):
        markup = back_to_main_menu_markup()
        text = CARD_RENAME_TEXT
        await state.set_state(states.CardRename.get_API)
        return dict(text=text, markup=markup)

    async def rename_card_get_api_key(self, state):
        text = 'Введите API-ключ.\n' \
               '<b>ВАЖНО!</b> Скопируйте ключ и вставьте его без лишних символов, ' \
               'иначе сменить название не получится.'
        markup = back_to_main_menu_markup()
        await state.set_state(states.CardRename.get_API)
        return dict(text=text, markup=markup)

    async def rename_card_get_supplier_id(self, state):
        text = 'Введите supplier-id.\n' \
               '<b>ВАЖНО!</b> Скопируйте id и вставьте его без лишних символов, ' \
               'иначе сменить название не получится.'
        markup = back_to_API_step()
        await state.set_state(states.CardRename.get_sup_id)
        return dict(text=text, markup=markup)

    async def rename_card_api_verification(self, message, state):
        if message.text.isascii():
            async with state.proxy() as proxy:
                proxy['api_key'] = message.text
            markup = back_to_API_step()
            text = 'Введите supplier-id.\n' \
                   '<b>ВАЖНО!</b> Скопируйте id и вставьте его без лишних символов, ' \
                   'иначе сменить название не получится.'
            await state.set_state(states.CardRename.get_sup_id)
        else:
            text = 'Вы ввели API-ключ неверного формата.\nПопробуйте снова.'
            markup = back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    async def rename_card_sup_id_verification(self, message, state):
        if message.text.isascii():
            async with state.proxy() as proxy:
                proxy['sup_id'] = message.text
            markup = back_to_supplierID_step()
            text = 'Введите артикул товара и новое название через пробел\n' \
                   '<b>Например</b> - 12345678 Свитер женский оверсайз'
            await state.set_state(states.CardRename.get_article_and_new_name)
        else:
            text = 'Вы ввели supplier-id неверного формата.\nПопробуйте снова.'
            markup = back_to_API_step()
        return dict(text=text, markup=markup)

    async def rename_card_get_article_and_name(self, state):
        markup = back_to_supplierID_step()
        text = 'Введите артикул товара и новое название через пробел\n' \
               '<b>Например</b> - 12345678 Свитер женский оверсайз'
        await state.set_state(states.CardRename.get_article_and_new_name)
        return dict(text=text, markup=markup)

    async def rename_card_article_and_name_verification(self, message, state):
        new_name_pattern = r'[0-9]{8,9}\s.+'
        if re.fullmatch(new_name_pattern, message.text):
            async with state.proxy() as proxy:
                proxy['article_and_new_name'] = message.text.split(' ', maxsplit=1)
            text = 'Все готово к смене наименования, пожалуйста, подождите.'
            markup = None
            is_valid = True
        else:
            text = '<b>Проверьте корректность введенного запроса.</b>\n'\
                   'Запрос должен состоять из артикула (8 или 9 цифр) и нового наименования,'\
                   ' разделенных пробелом.'
            markup = back_to_article_and_new_name_step()
            is_valid = False
        return dict(text=text, markup=markup, is_valid=is_valid)

    async def rename_card(self, state):
        async with state.proxy() as proxy:
            art_number = int(proxy['article_and_new_name'][0])
            new_name = proxy['article_and_new_name'][1]
            api_key = proxy['api_key']
            sup_id = proxy['sup_id']
        rename_is_success = await wb.rename_the_card(new_name, art_number, api_key, sup_id)
        if rename_is_success is error:
            text = 'Изменить наименование товара не получилось.\n' \
                   'Проверьте корректность ввода API-ключа или supplier-id.'
        elif rename_is_success:
            text = 'Замечательно! Ваше наименование успешно изменено.\n' \
                   'Название обновится в течение 20 минут.'
        else:
            text = 'Изменить наименование товара не получилось.\n' \
                   'Проверьте корректность ввода API-ключа или supplier-id.'
        await state.finish()
        markup = another_card_rename()
        return dict(text=text, markup=markup)

    async def instruction_bar(self):
        markup = back_to_main_menu_markup()
        text = f"{FAQ} {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
        return dict(text=text, markup=markup)
