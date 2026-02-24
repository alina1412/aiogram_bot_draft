from unittest.mock import AsyncMock

from aiogram.types import Chat, Message, User

from aio.handlers import echo_handler
from core.models import TgModel


async def test_echo_handler_integration(session):
    test_model = TgModel(id=1, chat_id=1234567890)
    session.add(test_model)
    await session.commit()

    message = AsyncMock(spec=Message)
    message.chat = AsyncMock(spec=Chat)
    message.chat.id = 12345
    message.text = "test message"
    message.from_user = User(id=67890, is_bot=False, first_name="Test")
    message.message_id = 1
    message.send_copy = AsyncMock()

    await echo_handler(message, session)

    message.send_copy.assert_called_once_with(chat_id=message.chat.id)
