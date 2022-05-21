from db.db_connector import Database
from . import markups
from logic.notification_service import Notification_Service
from . import states
from . import wildberries as wb
from . import mpstats
from const.phrases import FAQ
from const.const import *
import re
import os
from aiogram.utils.markdown import hlink
from aiogram import types


class Controller:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.notification = Notification_Service(bot=self.bot)

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
            text = f"Для доступа к функционалу бота подпишитесь на канал {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
            markup = markups.not_subscribed_markup()
            return dict(text=text, markup=markup)

        user = self.db.get_user(message.from_user.id)
        if user:
            name = message.from_user.first_name
            is_admin = self.db.check_for_admin(message.from_user.id)
            text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
            if is_admin:  # check for existing in db?
                markup = markups.admin_start_menu_markup()
            else:
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
            name = message.from_user.first_name
            text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
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
            name = message.from_user.first_name
            text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
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
            text = 'Спасибо за информацию! Теперь можешь собрать SEO.'
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
        async with state.proxy() as data:
            data['range_search'] = message.text.replace(' ', '$', 1).split('$')
        text = '🔎<b>Поиск запущен..</b> Результат скоро появится.'
        markup = markups.back_to_main_menu_markup()
        return dict(text=text, markup=markup)

    async def article_search(self, message, state):
        async with state.proxy() as data:
            if data['range_search'][0].isdigit() and len(data['range_search'][0]) == 8:
                position = wb.search_for_article(int(data['range_search'][0]), data['range_search'][1]) 
                if position:
                    text = f"Артикул {data['range_search'][0]} по запросу " \
                        f"{data['range_search'][1]} найден:\n\n" \
                        f"Страница {position[0]}\nПозиция {position[1]}"
                else:
                    text = 'Товара по данному запросу не обнаружено.'
            else:
                text = 'Товар не найден, проверьте корректность введенного артикула.'
        markup = markups.another_card_position_search_markup()
        await state.finish()
        return dict(text=text, markup=markup)
    
    async def category_for_price_segmentation(self, state):
        markup = markups.back_to_main_menu_markup()
        text = 'По какой категории определяем ценовую сегментацию?'
        await state.set_state(states.NameGroup.price_category)
        return dict(text=text, markup=markup)

    async def price_segmentation(self, message, state):
        if message.text == 'Назад в главное меню':
            name = message.from_user.first_name
            text = f'Приветствую, {name}! Это наш бот для улучшения твоей карточки на WB.'
            is_admin = self.db.check_for_admin(message.from_user.id)
            if is_admin:
                markup = markups.admin_start_menu_markup()
            else:
                markup = markups.start_menu_markup()
        else:
            path_to_excel = \
                mpstats.get_price_segmentation(query=message.text)
            if path_to_excel:
                text = 'Пожалуйста, ценовая сегментация для данной категории в таблице.'
                await message.answer_document(document=types.InputFile(path_to_excel))
                os.remove(path_to_excel)
                await state.finish()
            else:
                text = 'Вы ввели невалидную категорию.'
            markup = markups.another_price_segmentation_markup()
        return dict(text=text, markup=markup)

    async def instruction_bar(self):
        markup = markups.back_to_main_menu_markup()
        text = f"{FAQ} {hlink('OPTSHOP', 'https://t.me/opt_tyrke')}"
        return dict(text=text, markup=markup)
