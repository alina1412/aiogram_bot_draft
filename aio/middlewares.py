from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, types

from core.setup import get_session


class SessionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any],
    ) -> Any:
        async for session in get_session():
            data["session"] = session
            return await handler(event, data)


class ManagerMiddleware(BaseMiddleware):
    def __init__(self, manager):
        self.manager = manager
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any],
    ) -> Any:
        data["manager"] = self.manager
        return await handler(event, data)


class QueueMiddleware(BaseMiddleware):
    def __init__(self, queue_accessor):
        self.queue_accessor = queue_accessor
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
        event: types.Message,
        data: Dict[str, Any],
    ) -> Any:
        data["queue_accessor"] = self.queue_accessor
        return await handler(event, data)
