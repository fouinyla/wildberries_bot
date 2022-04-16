from .controller import Controller
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from os import getenv

#! temp
from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=getenv("BOT_TOKEN"))
Bot.set_current(bot)
dp = Dispatcher(bot, storage=MemoryStorage())
c = Controller(bot=bot)

# это меню старт
@dp.message_handler(commands='start')
@dp.message_handler(Text(equals='Назад в главное меню'))
async def command_start_process(message: types.Message):
    response = await c.command_start(message=message)
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )

# это меню "поисковой запрос"
@dp.message_handler(Text(equals='Поисковой запрос'))
async def search_query_process(message: types.Message):
    response = await c.search_query()
    await message.reply(
        text=response["text"],
        reply_markup=response["markup"],
        parse_mode="HTML",
        reply=False
    )


'''
@dp.message_handler(Text(equals="Notification")) 
async def message_main_menu_button_notification_process(message: types.Message):
    response = await c.message_main_menu_buttons_click(message=message)
    await message.reply(
        text=response["text"],
        parse_mode="HTML",
        reply=False
    )

@dp.message_handler(Text(contains="button"))
async def message_main_menu_buttons_click_process(message: types.Message):
    response = await c.message_main_menu_buttons_click(message=message)
    await message.reply(
        text=response["text"],
        parse_mode="HTML",
        reply=False
    )
'''