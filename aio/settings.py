from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from core.config import config

bot = Bot(
    token=config.bot.token
)  # , default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
