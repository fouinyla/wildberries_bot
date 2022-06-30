import logging
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware


class LoggingMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        print("here")
        logging.info("======= INCOMING UPDATE ========")
        logging.info(message)
