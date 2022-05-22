from urllib import response
from .controller import Controller
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
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


# это меню старт
@dp.message_handler(commands='start', state='*')
@dp.message_handler(Text(equals='Назад в главное меню'), state='*')
@dp.message_handler(Text(equals='Я подписался(-лась)'), state='*')
async def command_start_process(message: types.Message, state: FSMContext):
    response = await c.command_start(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это получение количества пользователей в БД для админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Количество пользователей в БД'), state='*')
async def get_number_of_users_process(message: types.Message):
    response = await c.get_number_of_users()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это выгрузка из БД для админа
@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Полная выгрузка из БД'), state='*')
async def get_data_from_db_process(message: types.Message):
    response = await c.get_data_from_db(message=message)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это запрос tg_id для добавления нового админа


@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Добавить админа'), state='*')
async def pre_step_for_add_admin_process(message: types.Message, state: FSMContext):
    response = await c.pre_step_for_add_admin(state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это добавление нового админа


@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    state=states.Admin.tg_id_to_add)
async def add_admin_process(message: types.Message, state: FSMContext):
    response = await c.add_admin(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это запрос tg_id для удаления старого админа


@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    Text(equals='Удалить админа'), state='*')
async def pre_step_for_delete_admin_process(message: types.Message, state: FSMContext):
    response = await c.pre_step_for_delete_admin(state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это удаление старого админа


@dp.message_handler(lambda message: database.check_for_admin(message.from_user.id),
                    state=states.Admin.tg_id_to_delete)
async def delete_admin_process(message: types.Message, state: FSMContext):
    response = await c.delete_admin(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# Сбор данных пользователя


@dp.message_handler(state=states.User.name)
async def process_name(message: types.Message, state: FSMContext):
    response = await c.message_name_state(message=message, state=state)
    await message.reply(
        text=response['text'],
        reply_markup=response['markup'],
        reply=False
    )


@dp.message_handler(state=states.User.email)
async def process_email(message: types.Message, state: FSMContext):
    response = await c.message_email_state(message=message, state=state)
    await message.reply(
        text=response['text'],
        reply_markup=response['markup'],
        reply=False
    )


@dp.message_handler(state=states.User.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):
    response = await c.message_phone_number_state(message=message, state=state)
    await message.reply(
        text=response['text'],
        reply_markup=response['markup'],
        reply=False
    )


# это меню "поисковой запрос"
@dp.message_handler(Text(equals='Поисковой запрос'), state='*')
@dp.message_handler(Text(equals='Ввести поисковой запрос повторно'), state='*')
async def search_query_process(message: types.Message, state: FSMContext):
    response = await c.search_query(state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это меню получение поискового запроса
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.query)
async def giving_hints_process(message: types.Message, state: FSMContext):
    response = await c.giving_hints(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это меню "Сбор SEO ядра"
@dp.message_handler(Text(equals='Сбор SEO ядра'), state='*')
@dp.message_handler(Text(equals='Собрать SEO повторно'), state='*')
async def building_seo_core_process(message: types.Message, state: FSMContext):
    response = await c.building_seo_core(state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это ответ (ожидание) после передачи запросов для SEO
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.SEO_queries)
async def waiting_seo_result_process(message: types.Message, state: FSMContext):
    response = await c.waiting_seo_result(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )
    response = await c.building_seo_result(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это меню "ценовая сегментация"
@dp.message_handler(Text(equals='Ценовая сегментация'), state='*')
@dp.message_handler(Text(equals='Узнать ценовую сегментацию повторно'), state='*')
async def category_for_price_segmentation_process(message: types.Message, state: FSMContext):
    response = await c.category_for_price_segmentation(state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это выдача результатов "ценовая сегментация"
@dp.callback_query_handler()
async def callback_price_segmentation_process(query: types.CallbackQuery):
    response = await c.callback_price_segmentation(query=query)
    if response:
        await bot.send_message(
            chat_id=query.from_user.id, 
            text=response['text'], 
            reply_markup=response['markup'], 
            parse_mode='HTML'
        )


# это меню поиска позиции
@dp.message_handler(Text(equals='Поиск по ранжированию'), state='*')
@dp.message_handler(Text(equals='Ввести запрос повторно'), state='*')
async def card_position_search(message: types.Message, state: FSMContext):
    response = await c.position_search(state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это меню ожидания и выдачи позиции товара
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.range_search)
async def card_article_search(message: types.Message, state: FSMContext):
    response = await c.waiting_for_article_search(message, state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )
    response = await c.article_search(message, state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это меню 'Как пользоваться ботом'
@dp.message_handler(Text(equals='Как пользоваться ботом'))
async def instruction_bar_process(message: types.Message):
    response = await c.instruction_bar()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )
