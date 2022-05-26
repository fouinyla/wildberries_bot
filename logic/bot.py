from .controller import Controller
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from os import getenv
from . import states
from db.db_connector import Database


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


# получение количества пользователей в БД для админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Количество пользователей в БД'), state='*')
async def get_number_of_users_process(message: Message):
    response = await c.get_number_of_users()
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# выгрузка из БД для админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Полная выгрузка из БД'), state='*')
async def get_data_from_db_process(message: Message):
    response = await c.get_data_from_db(message=message)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# запрос tg_id для добавления нового админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Добавить админа'), state='*')
async def pre_step_for_add_admin_process(message: Message, state: FSMContext):
    response = await c.pre_step_for_add_admin(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# добавление нового админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    state=states.Admin.tg_id_to_add)
async def add_admin_process(message: Message, state: FSMContext):
    response = await c.add_admin(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# запрос tg_id для удаления старого админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Удалить админа'), state='*')
async def pre_step_for_delete_admin_process(message: Message, state: FSMContext):
    response = await c.pre_step_for_delete_admin(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

# удаление старого админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    state=states.Admin.tg_id_to_delete)
async def delete_admin_process(message: Message, state: FSMContext):
    response = await c.delete_admin(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

# запрос сообщения для рассылки на всех пользователей
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Рассылка на всех пользователей'), state='*')
async def pre_step_for_mailing_to_clients_process(message: Message, state: FSMContext):
    response = await c.pre_step_for_mailing_to_clients(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

# подтверждение рассылки на всех пользователей
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id) and \
                    message.text != 'Да, отправляй',
                    state=states.Admin.message_to_clients)
async def confirmation_mailing_to_clients_process(message: Message, state: FSMContext):
    response = await c.confirmation_mailing_to_clients(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
                
# рассылка на всех пользователей
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id) and \
                    message.text == 'Да, отправляй',
                    state=states.Admin.message_to_clients)
async def mailing_to_clients_process(message: Message, state: FSMContext):
    response = await c.mailing_to_clients(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

# Сбор данных пользователя
@dp.message_handler(state=states.User.name)
async def process_name(message: Message, state: FSMContext):
    response = await c.message_name_state(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)

@dp.message_handler(state=states.User.email)
async def process_email(message: Message, state: FSMContext):
    response = await c.message_email_state(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


@dp.message_handler(state=states.User.phone_number)
async def process_phone_number(message: Message, state: FSMContext):
    response = await c.message_phone_number_state(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню "поисковой запрос"
@dp.message_handler(Text(equals='Поисковой запрос'), state='*')
@dp.message_handler(Text(equals='Ввести поисковой запрос повторно'), state='*')
async def search_query_process(message: Message, state: FSMContext):
    response = await c.search_query(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню получение поискового запроса
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.query)
async def giving_hints_process(message: Message, state: FSMContext):
    response = await c.giving_hints(message=message, state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# меню "Сбор SEO ядра"
@dp.message_handler(Text(equals='Сбор SEO ядра'), state='*')
@dp.message_handler(Text(equals='Собрать SEO повторно'), state='*')
async def building_seo_core_process(message: Message, state: FSMContext):
    response = await c.building_seo_core(state=state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# ответ (ожидание) после передачи запросов для SEO
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.SEO_queries)
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
@dp.message_handler(Text(equals='Ценовая сегментация'), state='*')
@dp.message_handler(Text(equals='Узнать ценовую сегментацию повторно'), state='*')
@dp.message_handler(Text(equals='Получить график'), state='*')
@dp.message_handler(Text(equals='Получить другой график'), state='*')
async def category_selection_process(message: Message, state: FSMContext):
    if 'график' in message.text:
        await state.set_state(states.TrendGraph.category_selection)
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
@dp.callback_query_handler(state=states.TrendGraph.category_selection)
async def callback_graph_category_selection_process(query: CallbackQuery, state: FSMContext):
    response = await c.callback_graph_category_selection(query=query, state=state)
    if not response:
        return None
    await state.set_state(states.TrendGraph.view_selection)
    await bot.send_message(chat_id=query.from_user.id,
                           text=response['text'],
                           reply_markup=response['markup'],
                           parse_mode='HTML')


# выбрали view -> предлагаем выбрать value
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.TrendGraph.view_selection)
async def graph_view_selection_process(message: Message, state: FSMContext):
    response = await c.graph_view_selection(message=message, state=state)
    await state.set_state(states.TrendGraph.value_selection)
    await bot.send_message(chat_id=message.from_user.id,
                           text=response['text'],
                           reply_markup=response['markup'],
                           parse_mode='HTML')


# выбрали value -> предлагаем ввести date_1
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.TrendGraph.value_selection)
async def graph_value_selection_process(message: Message, state: FSMContext):
    response = await c.graph_value_selection(message=message, state=state)
    await state.set_state(states.TrendGraph.date_1_selection)
    await bot.send_message(chat_id=message.from_user.id,
                           text=response['text'],
                           reply_markup=response['markup'],
                           parse_mode='HTML')


# ввели date_1 -> предлагаем ввести date_2
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.TrendGraph.date_1_selection)
async def graph_date_1_selection_process(message: Message, state: FSMContext):
    response = await c.graph_date_1_selection(message=message, state=state)
    await state.set_state(states.TrendGraph.date_2_selection)
    await bot.send_message(chat_id=message.from_user.id,
                           text=response['text'],
                           reply_markup=response['markup'],
                           parse_mode='HTML')


# выбрали date_2 -> выдаем график
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.TrendGraph.date_2_selection)
async def graph_date_2_selection_process(message: Message, state: FSMContext):
    response = await c.graph_date_2_selection(message=message, state=state)
    await state.finish()
    await bot.send_message(chat_id=message.from_user.id,
                           text=response['text'],
                           reply_markup=response['markup'],
                           parse_mode='HTML')
# _____________________окончание логики по выдаче графиков_____________________


# меню поиска позиции
@dp.message_handler(Text(equals='Поиск по ранжированию'), state='*')
@dp.message_handler(Text(equals='Ввести запрос повторно'), state='*')
async def card_position_search(message: Message, state: FSMContext):
    response = await c.position_search(state)
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)


# это меню ожидания и выдачи позиции товара
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.range_search)
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


# это меню 'Как пользоваться ботом'
@dp.message_handler(Text(equals='Как пользоваться ботом'))
async def instruction_bar_process(message: Message):
    response = await c.instruction_bar()
    await message.reply(text=response['text'],
                        reply_markup=response['markup'],
                        parse_mode='HTML',
                        reply=False)
