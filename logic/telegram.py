import aiogram

CUSTOMER_CHANNEL_ID = '@opt_tyrke'


async def subscribed(bot: aiogram.Bot, user_id: int) -> bool:
    """
    Checks if the user is subscribed to the customer's channel.
    """
    status = await bot.get_chat_member(chat_id=CUSTOMER_CHANNEL_ID,
                                       user_id=user_id)
    return status['status'] != 'left'
