import asyncio

from aio.handlers import *
from aio.manager import MessageManager
from aio.middlewares import (
    ManagerMiddleware,
    QueueMiddleware,
    SessionMiddleware,
)
from aio.settings import bot, dp
from core.config import config
from rabbit_service.rabbit import QueueAccessor

message_manager = MessageManager(bot)
queue_accessor = QueueAccessor(message_manager)

dp.message.middleware(SessionMiddleware())
dp.message.middleware(ManagerMiddleware(message_manager))
dp.message.middleware(QueueMiddleware(queue_accessor))


async def bot_start():
    await dp.start_polling(bot, handle_signals=False)


async def rabbit_start() -> None:
    work_task2 = asyncio.create_task(queue_accessor.receive_from_queue())


async def stop():
    config.logger.warning("Stopping rabbit on KeyboardInterrupt...")
    await queue_accessor.disconnect()


async def main():
    try:
        await asyncio.gather(
            bot_start(),
            rabbit_start(),
        )
    finally:
        await stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # The finally block in main() will handle cleanup
        pass
