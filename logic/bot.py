from .controller import Controller
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from os import getenv
from .states import CardRename, NameGroup, User, Admin, TrendGraph
from db.db_connector import Database
from . import memory


# temp
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=getenv('BOT_TOKEN'))
Bot.set_current(bot)
dp = Dispatcher(bot, storage=MemoryStorage())
c = Controller(bot=bot)
database = Database()


# меню старт
@dp.message_handler(commands='start', state='*')
@dp.message_handler(Text(equals='Назад в главное меню'), state='*')
@dp.message_handler(Text(equals='Я подписался(-лась)'), state='*')
async def command_start_process(message: Message, state: FSMContext):
    response = await c.command_start(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# это меню админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    Text(equals='Функции админа'), state='*')
@dp.message_handler(Text(equals='Назад в меню админа'), state='*')
async def admin_menu_process(message: Message, state: FSMContext):
    response = await c.admin_menu(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# получение количества пользователей в БД для админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    Text(equals='Количество пользователей в БД'), state='*')
async def get_number_of_users_process(message: Message):
    response = await c.get_number_of_users()
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# выгрузка из БД для админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    Text(equals='Полная выгрузка из БД'), state='*')
async def get_data_from_db_process(message: Message):
    response = await c.get_data_from_db(message=message)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# запрос tg_id для добавления нового админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    Text(equals='Добавить админа'), state='*')
async def pre_step_for_add_admin_process(message: Message, state: FSMContext):
    response = await c.pre_step_for_add_admin(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# добавление нового админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    state=Admin.tg_id_to_add)
async def add_admin_process(message: Message, state: FSMContext):
    response = await c.add_admin(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# запрос tg_id для удаления старого админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    Text(equals='Удалить админа'), state='*')
async def pre_step_for_delete_admin_process(message: Message, state: FSMContext):
    response = await c.pre_step_for_delete_admin(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# удаление старого админа
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    state=Admin.tg_id_to_delete)
async def delete_admin_process(message: Message, state: FSMContext):
    response = await c.delete_admin(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# запрос сообщения для рассылки на всех пользователей
@dp.message_handler(lambda message: message.from_user.id in memory.admins,
                    Text(equals='Рассылка на всех пользователей'), state='*')
async def pre_step_for_mailing_to_clients_process(message: Message, state: FSMContext):
    response = await c.pre_step_for_mailing_to_clients(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# подтверждение рассылки на всех пользователей
@dp.message_handler(lambda message: message.from_user.id in memory.admins and \
                    message.text != 'Да, отправляй',
                    state=Admin.message_to_clients)
async def confirmation_mailing_to_clients_process(message: Message, state: FSMContext):
    response = await c.confirmation_mailing_to_clients(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# рассылка на всех пользователей
@dp.message_handler(lambda message: message.from_user.id in memory.admins and \
                    message.text == 'Да, отправляй',
                    state=Admin.message_to_clients)
async def mailing_to_clients_process(message: Message, state: FSMContext):
    response = await c.mailing_to_clients(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# Сбор данных пользователя
@dp.message_handler(state=User.name)
async def process_name(message: Message, state: FSMContext):
    response = await c.message_name_state(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


@dp.message_handler(state=User.email)
async def process_email(message: Message, state: FSMContext):
    response = await c.message_email_state(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


@dp.message_handler(state=User.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    response = await c.message_phone_number_state(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню "поисковой запрос"
@dp.message_handler(commands='query', state='*')
@dp.message_handler(Text(equals='Поисковой запрос'), state='*')
@dp.message_handler(Text(equals='Ввести поисковой запрос повторно'), state='*')
async def search_query_process(message: Message, state: FSMContext):
    response = await c.search_query(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню получение поискового запроса
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=NameGroup.query)
async def giving_hints_process(message: Message, state: FSMContext):
    response = await c.giving_hints(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню "Сбор SEO ядра"
@dp.message_handler(commands='seo', state='*')
@dp.message_handler(Text(equals='Сбор SEO ядра'), state='*')
@dp.message_handler(Text(equals='Собрать SEO повторно'), state='*')
async def building_seo_core_process(message: Message, state: FSMContext):
    response = await c.building_seo_core(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# ответ (ожидание) после передачи запросов для SEO
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=NameGroup.SEO_queries)
async def waiting_seo_result_process(message: Message, state: FSMContext):
    response = await c.waiting_seo_result(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    response = await c.building_seo_result(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# выбор категории с помощью inline кнопок
@dp.message_handler(commands='prices', state='*')
@dp.message_handler(commands='graph', state='*')
@dp.message_handler(Text(equals='Ценовая сегментация'), state='*')
@dp.message_handler(Text(equals='Узнать ценовую сегментацию повторно'), state='*')
@dp.message_handler(Text(equals='Получить график'), state='*')
@dp.message_handler(Text(equals='Получить другой график'), state='*')
async def category_selection_process(message: Message, state: FSMContext):
    if 'график' in message.text or 'graph' in message.text:
        await state.set_state(TrendGraph.category_selection)
    response = await c.category_selection(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# выдача результатов "ценовая сегментация"
@dp.callback_query_handler()
async def callback_price_segmentation_process(query: CallbackQuery):
    response = await c.callback_price_segmentation(query=query)
    if not response:
        return None
    await bot.send_message(chat_id=query.from_user.id,
                           text=response['text'],
                           reply_markup=response['markup'],
                           parse_mode='HTML')


# __________________________логика по выдаче графика__________________________
# выбираем category для выдачи графика -> предлагаем выбрать view
@dp.callback_query_handler(state=TrendGraph.category_selection)
async def callback_graph_category_selection_process(query: CallbackQuery, state: FSMContext):
    successful_step = await c.callback_graph_category_selection(query, state)
    if successful_step:
        await state.set_state(TrendGraph.view_selection)


# выбрали view -> предлагаем выбрать value
@dp.message_handler(lambda x: not str(x).startswith('Назад'),
                    state=TrendGraph.view_selection)
async def graph_view_selection_process(message: Message, state: FSMContext):
    successful_step = await c.graph_view_selection(message, state)
    if successful_step:
        await state.set_state(TrendGraph.value_selection)


# выбрали value -> предлагаем ввести date_1
@dp.message_handler(lambda x: not str(x).startswith('Назад'),
                    state=TrendGraph.value_selection)
async def graph_value_selection_process(message: Message, state: FSMContext):
    successful_step = await c.graph_value_selection(message, state)
    if successful_step is None:
        await state.finish()
    if successful_step:
        await state.set_state(TrendGraph.date_1_selection)


# ввели date_1 -> предлагаем ввести date_2
@dp.message_handler(lambda x: not str(x).startswith('Назад'),
                    state=TrendGraph.date_1_selection)
async def graph_date_1_selection_process(message: Message, state: FSMContext):
    successful_step = await c.graph_date_1_selection(message, state)
    if successful_step:
        await state.set_state(TrendGraph.date_2_selection)


# выбрали date_2 -> выдаем график
@dp.message_handler(lambda x: not str(x).startswith('Назад'),
                    state=TrendGraph.date_2_selection)
async def graph_date_2_selection_process(message: Message, state: FSMContext):
    successful_step = await c.graph_date_2_selection(message, state)
    if successful_step:
        await state.finish()
# _____________________окончание логики по выдаче графиков_____________________


# меню поиска позиции
@dp.message_handler(commands='search', state='*')
@dp.message_handler(Text(equals='Поиск по ранжированию'), state='*')
@dp.message_handler(Text(equals='Ввести запрос повторно'), state='*')
async def card_position_search(message: Message, state: FSMContext):
    response = await c.position_search(state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# это меню ожидания и выдачи позиции товара
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=NameGroup.range_search)
async def card_article_search(message: Message, state: FSMContext):
    response = await c.waiting_for_article_search(message, state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    if response['is_valid_query']:
        response = await c.article_search(message, state)
        await message.reply(text=response['text'],
                            reply_markup=response['markup'],
                            parse_mode='HTML',
                            reply=False)


# это запрос артикула для 'Продажи по артикулу'
@dp.message_handler(commands='sales', state='*')
@dp.message_handler(Text(equals='Продажи по артикулу'), state='*')
@dp.message_handler(Text(equals='Узнать продажи по артикулу повторно'), state='*')
async def get_article_month_sales_process(message: Message, state: FSMContext):
    response = await c.get_article_month_sales(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# это выдача данных для 'Продажи по артикулу'
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=NameGroup.article_for_sales)
async def waiting_month_sales_process(message: Message, state: FSMContext):
    response = await c.waiting_month_sales(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    if response['is_valid_article']:
        response = await c.ploting_graph_month_sales(message=message, state=state)
        await message.reply(text=response['text'],
                            reply_markup=response['markup'],
                            parse_mode='HTML',
                            reply=False)


# это запрос артикула для 'Позиция карточки при запросах'
@dp.message_handler(commands='card_search', state='*')
@dp.message_handler(Text(equals='Позиция карточки при запросах'), state='*')
@dp.message_handler(Text(equals='Узнать позицию по артикулу повторно'), state='*')
async def get_article_card_queries_process(message: Message, state: FSMContext):
    response = await c.get_article_card_queries(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# это выдача данных для 'Позиция карточки при запросах'
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=NameGroup.article_for_queries)
async def creating_queries_table_process(message: Message, state: FSMContext):
    response = await c.waiting_queries_table(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
    if response['is_valid_article']:
        response = await c.creating_queries_table(message=message, state=state)
        await message.reply(text=response['text'],
                            reply_markup=response['markup'],
                            parse_mode='HTML',
                            reply=False)


# ___________________начало логики смены названия карточки___________________
# меню получения API-ключа
@dp.message_handler(commands='rename', state='*')
@dp.message_handler(Text(equals='Сменить название товара'), state='*')
@dp.message_handler(Text(equals='Назад к вводу API-ключа'), state='*')
async def rename_card_API_ask_process(message: Message, state: FSMContext):
    response = await c.rename_card_API_ask(state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню получения supplier-id
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=CardRename.get_API)
@dp.message_handler(Text(equals='Назад к вводу supplier-id'), state='*')
async def rename_card_supplierID_ask_process(message: Message, state: FSMContext):
    response = await c.rename_card_supplierID_ask(message, state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню получения артикула и нового имени
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=CardRename.get_supID)
@dp.message_handler(Text(equals='Назад к вводу артикула и наименования'), state='*')
async def rename_card_article_and_name_ask_process(message: Message, state: FSMContext):
    response = await c.rename_card_article_and_name_ask(message, state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# основное меню смены названия
@dp.message_handler(lambda x: not str(x.text).startswith(('Назад', '/')), state=CardRename.get_article_and_new_name)
@dp.message_handler(Text(equals='Сменить наименование повторно'), state='*')
async def rename_card_process(message: Message, state: FSMContext):
    response = await c.rename_card(message, state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
# __________________окончание логики смены названия карточки__________________


# это меню 'Как пользоваться ботом'
@dp.message_handler(commands='help', state='*')
@dp.message_handler(Text(equals='Как пользоваться ботом'))
async def instruction_bar_process(message: Message):
    response = await c.instruction_bar()
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
