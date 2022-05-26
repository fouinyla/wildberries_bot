from math import ceil
from const import phrases
from .utils import get_callback
from . import markups
import json
from aiogram import types


class InlineCallback():
    def __init__(self, bot):
        self.bot = bot

    async def process_callback(self, query):
        data = get_callback(query.data)
        action = data["a"]
        if action == '.':
            await self.bot.answer_callback_query(
                callback_query_id=query.id
            )
        elif action == "SCT":
            cat_id = data["d"]
            cat_json = json.load(open("static/cats/" + cat_id.rsplit('.', cat_id.count('.')-1)[0] + ".json"))
            path = cat_json[cat_id]
            text = f'Вы выбрали категорию <b>{path}</b>'
            markup = None
            await self.edit_message(
                query=query,
                text=text,
                markup=markup
            )
            return path

        elif action == "PCK":
            cat_id = data["d"]
            if cat_id.count('.') == 3:
                cat_json = json.load(open("static/cats/" + cat_id.rsplit('.', cat_id.count('.')-1)[0] + ".json"))
                path = cat_json[cat_id]
                text = f'Вы выбрали категорию <b>{path}</b>.\nПодождите немного, мы подготавливаем результат.'
                markup = None
                await self.edit_message(
                    query=query,
                    text=text,
                    markup=markup
                )
                return path

            cat_json = json.load(open("static/cats/"+(cat_id if cat_id.count('.') <= 1 else cat_id.rsplit('.', 1)[0])+".json"))
            subcats = [dict(id=key, name=value.split('/')[-1]) for key, value in cat_json.items() if key.startswith(cat_id) and key.count('.') == (cat_id.count('.') + 1)]

            text = phrases.phrase_for_categories_inline_keyboard(
                data=dict(
                    category=(cat_json[cat_id] if not cat_id == '0' else ""),
                    current_page=1,
                    total_page=ceil(len(subcats)/10)
                )
            )
            markup = markups.inline_categories_markup(
                categories=subcats[:10],
                cat_id=cat_id,
                next_page=(2 if len(subcats) > 10 else False),
                back_to=(cat_id.rsplit('.', 1)[0] if cat_id.count('.') > 0 else False),
                select=not (cat_id.count('.') == 0)
            )
            await self.edit_message(
                query=query,
                text=text,
                markup=markup
            )

        elif action == "NXT":
            cat_id = data["d"]
            page = data["p"]
            cat_json = json.load(open("static/cats/"+(cat_id if cat_id.count('.') <= 1 else cat_id.rsplit('.', 1)[0])+".json"))
            siblings = [dict(id=key, name=value.split('/')[-1]) for key, value in cat_json.items() if key.startswith(cat_id) and key.count('.') == (cat_id.count('.') + 1)]
            text = phrases.phrase_for_categories_inline_keyboard(
                data=dict(
                    category=("" if cat_id == "0" else cat_json[cat_id]),
                    current_page=page,
                    total_page=ceil(len(siblings)/10)
                )
            )
            markup = markups.inline_categories_markup(
                categories=siblings[10*(page-1):10*(page)],
                cat_id=cat_id,
                prev_page=page-1,
                next_page=(page+1 if len(siblings[10*(page-1):]) > 10 else False),
                back_to=(cat_id.rsplit('.', 1)[0] if cat_id.count('.') > 1 else False),
                select=not (cat_id.count('.') == 0)
            )
            await self.edit_message(
                query=query,
                text=text,
                markup=markup
            )

        elif action == "PRV":
            cat_id = data["d"]
            page = data["p"]
            cat_json = json.load(open("static/cats/"+(cat_id if cat_id.count('.') <= 1 else cat_id.rsplit('.', 1)[0])+".json"))
            siblings = [dict(id=key, name=value.split('/')[-1]) for key, value in cat_json.items() if key.startswith(cat_id) and key.count('.') == (cat_id.count('.') + 1)]

            text = phrases.phrase_for_categories_inline_keyboard(
                data=dict(
                    category=("" if cat_id == "0" else cat_json[cat_id]),
                    current_page=page,
                    total_page=ceil(len(siblings)/10)
                )
            )
            markup = markups.inline_categories_markup(
                categories=siblings[10*(page-1):10*(page)],
                cat_id=cat_id,
                prev_page=page-1,
                next_page=(page+1 if len(siblings[10*(page-1):]) > 10 else False),
                back_to=(cat_id.rsplit('.', 1)[0] if cat_id.count('.') > 1 else False),
                select=not (cat_id.count('.') == 0)
            )
            await self.edit_message(
                query=query,
                text=text,
                markup=markup
            )

        elif action == "ABR":
            text = "Главное меню"
            markup = None
            await self.edit_message(
                query=query,
                text=text,
                markup=markup
            )

    async def edit_message(self, query, text, markup):
        await self.bot.edit_message_text(
            text=text,
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            reply_markup=markup,
            parse_mode="HTML"
        )

    async def alert(self, query, text):
        await self.bot.answer_callback_query(
            callback_query_id=query.id,
            text=text,
            show_alert=True
        )
