import asyncio

from aio.handlers import *
from aio.manager import MessageManager
from aio.middlewares import SessionMiddleware
from aio.settings import bot, dp
from core.config import config
from rabbit_service.rabbit import QueueAccessor

dp.message.middleware(SessionMiddleware())


message_manager = MessageManager()
queue = QueueAccessor(message_manager)


async def bot_start():
    await dp.start_polling(bot, handle_signals=False)


async def rabbit_start() -> None:
    work_task2 = asyncio.create_task(queue.receive_from_queue())


async def stop():
    config.logger.warning("Stopping rabbit on KeyboardInterrupt...")
    await queue.disconnect()


async def main():
    try:
        await asyncio.gather(
            asyncio.create_task(bot_start()),
            asyncio.create_task(rabbit_start()),
        )
    finally:
        await stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # The finally block in main() will handle cleanup
        pass
