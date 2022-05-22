from datetime import datetime
from const import phrases
from .. import utils
from . import inline_calendar


class InlineCallback():
    def __init__(self, notification_service, bot, db, scheduler):
        self.ns = notification_service
        self.bot = bot
        self.db = db
        self.scheduler = scheduler

    async def process_callback(self, query):
        data = utils.get_callback(query.data)
        action = data["a"]
        if action == "FLR":
            response = await inline_calendar.action_create_calendar_markup(
                location=data["l"]
            )
            await self.edit_message(query=query, response=response)

        elif action == "DAY":
            response = await inline_calendar.action_create_time_markup(
                data=data,
                db=self.db
            )
            await self.edit_message(query=query, response=response)

        elif action == "TM":
            response = await inline_calendar.action_book_training(
                query=query,
                data=data,
                db=self.db,
                ns=self.ns
            )
            if response["notification"]:
                await self.ns.notify_admin_about_booking_training(
                    data=response["notification"]
                )
                t = datetime.strptime(data["t"], "%H:%M").time()
                self.scheduler.run_tasks(
                    task_list=[
                        self.scheduler.create_training_reminder_task(
                            data=dict(
                                time=t,
                                tg_id=response["tg_id"],
                                user_name=response["notification"]["name"]
                            )
                        ),
                        self.scheduler.create_admin_check_user_participation_task(
                            data=dict(
                                time=t,
                                tg_id=response["tg_id"],
                                user_name=response["notification"]["name"],
                                user_nickname=response["notification"]["user_tg_nickname"],
                                training_id=response["training_id"]
                            )
                        )
                    ]
                )
            if not response["markup"] == "SAME":
                await self.edit_message(query=query, response=response)
            if response["popup_text"]:
                await self.alert(query=query, text=response["popup_text"])

        elif action == "ABR":  # ? ABoRt
            response = await inline_calendar.action_abort()
            await self.edit_message(query=query, response=response)

        elif action == "AFC":  # ? Abortion From Calendar
            response = await inline_calendar.action_abort_from_calendar()
            await self.edit_message(query=query, response=response)

        elif action == "AUP":  # ? Approve User Participation
            self.db.set_training_attendance(
                training_id=data["t"],
                attendance=True
            )
            response = self.db.get_users_used_training_count(tg_id=data["i"])
            if response["trainings_count"] - response["used_trainings_count"] == 1:
                await self.ns.notify_user_about_one_training_left(
                    data=dict(
                        name=response["name"],
                        tg_id=data["i"]
                    )
                )
            elif response["trainings_count"] == response["used_trainings_count"]:
                self.db.disable_subscription(subscription_id=response["subscription_id"])
                await self.ns.notify_user_about_subscription_disabled(
                    data=dict(
                        name=response["name"],
                        tg_id=data["i"]
                    )
                )
            await self.edit_message(
                query=query,
                response=dict(
                    text=phrases.phrase_for_notify_that_training_is_taken_off(
                        data=dict(
                            user_nickname=response["tg_nickname"]
                        )
                    ),
                    markup=None
                )
            )

        elif action == "DUP":  # ? Decline User Participation
            response = self.db.get_user(tg_id=data["i"])
            self.db.set_training_attendance(
                training_id=data["t"],
                attendance=False
            )
            await self.edit_message(
                query=query,
                response=dict(
                    text=phrases.phrase_for_notify_that_training_is_not_taken_off(
                        data=dict(
                            user_nickname=response["tg_nickname"]
                        )
                    ),
                    markup=None
                )
            )

        await query.answer()

    async def edit_message(self, query, response):
        await self.bot.edit_message_text(
            text=response["text"],
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            reply_markup=response["markup"],
            parse_mode="HTML"
        )

    async def alert(self, query, text):
        await self.bot.answer_callback_query(
            callback_query_id=query.id,
            text=text,
            show_alert=True
        )
