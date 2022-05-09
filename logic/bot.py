from .controller import Controller
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from os import getenv
from . import states

# temp
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=getenv('BOT_TOKEN'))
Bot.set_current(bot)
dp = Dispatcher(bot, storage=MemoryStorage())
c = Controller(bot=bot)


# это меню старт
@dp.message_handler(commands='start', state='*')
@dp.message_handler(Text(equals='Назад в главное меню'), state='*')
async def command_start_process(message: types.Message, state: FSMContext):
    response = await c.command_start(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# Сбор данных пользователя
@dp.message_handler(state=states.User.name)
async def process_name(message, state):
    response = await c.message_name_state(message=message, state=state)
    await message.reply(
        text=response['text'],
        reply_markup=response['markup'],
        reply=False
    )


@dp.message_handler(state=states.User.email)
async def process_email(message, state):
    response = await c.message_email_state(message=message, state=state)
    await message.reply(
        text=response['text'],
        reply_markup=response['markup'],
        reply=False
    )


@dp.message_handler(state=states.User.phone_number)
async def process_phone_number(message, state):
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
    response = await c.search_query(state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это меню получение поискового запроса
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.query)
async def giving_hints_process(message: types.Message, state: FSMContext):
    response = await c.giving_hints(message, state)
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
    response = await c.building_seo_core(state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


# это ответ (ожидание) после передачи запросов для SEO
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.SEO_queries)
async def waiting_seo_result_process(message: types.Message, state: FSMContext):
    response = await c.waiting_seo_result(message, state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )
    response = await c.building_seo_result(message, state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    ) 


# это меню "FAQ"
@dp.message_handler(Text(equals='Как пользоваться ботом'))
async def instruction_bar_process(message: types.Message):
    response = await c.instruction_bar()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )
