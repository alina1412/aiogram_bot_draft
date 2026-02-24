import asyncio

from aio.handlers import *
from aio.middlewares import SessionMiddleware
from aio.settings import bot, dp

dp.message.middleware(SessionMiddleware())


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
