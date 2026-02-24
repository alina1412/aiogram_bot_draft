from typing import List

from aiogram.client.default import DefaultBotProperties
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select

from core.models import TgModel


class MyCallback(CallbackData, prefix="my"):
    action: str


def get_inline_keyboard():
    """List of lists, second row - second list"""
    buttons = [
        [
            InlineKeyboardButton(
                text="Button 1",
                callback_data=MyCallback(action="button1").pack(),
            ),
            InlineKeyboardButton(
                text="Button 2",
                callback_data=MyCallback(action="button2").pack(),
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def get_from_tg_table(session) -> List[TgModel]:
    return (await session.execute(select(TgModel))).scalars().all()
