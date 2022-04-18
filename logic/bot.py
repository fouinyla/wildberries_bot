from .controller import Controller
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from os import getenv
from . import states

#! temp
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=getenv("BOT_TOKEN"))
Bot.set_current(bot)
dp = Dispatcher(bot, storage=MemoryStorage())
c = Controller(bot=bot)

# это меню старт
@dp.message_handler(commands='start')
@dp.message_handler(Text(equals='Назад в главное меню'), state='*')
async def command_start_process(message: types.Message, state: FSMContext):
    response = await c.command_start(message=message, state=state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это меню "поисковой запрос"
@dp.message_handler(Text(equals='Поисковой запрос'))
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
async def building_seo_core_process(message: types.Message, state: FSMContext):
    response = await c.building_seo_core(state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это ответ после передачи запросов для SEO
@dp.message_handler(lambda x: not str(x).startswith('Назад'), state=states.NameGroup.SEO_queries)
async def building_seo_result_process(message: types.Message, state: FSMContext):
    response = await c.building_seo_result(message, state)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это меню "Прочее"
@dp.message_handler(Text(equals='Прочее'))
@dp.message_handler(Text(equals='Назад в меню прочее'))
async def other_menu_process(message: types.Message):
    response = await c.other_menu()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это меню "Оплата"
@dp.message_handler(Text(equals='Оплата'))
async def bot_payment_process(message: types.Message):
    response = await c.bot_payment()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это меню "FAQ"
@dp.message_handler(Text(equals='FAQ'))
async def FAQ_bar_process(message: types.Message):
    response = await c.FAQ_bar()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )
