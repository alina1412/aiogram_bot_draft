import json

from aiogram import exceptions, types

from core.config import config


class MessageManager:
    """Manages sending messages through Telegram bot."""

    def __init__(self, bot):
        self.bot = bot
        self.logger = config.logger

    async def handle_updates(self, message_dict: dict) -> None:
        self.logger.info("handle_updates %s", message_dict)
        text = json.dumps(message_dict)

        if "chat_id" in message_dict:
            chat_id = message_dict["chat_id"]
        else:
            self.logger.error(f"rabbit message not transferred {text}")
            return

        await self.send_message(user_id=chat_id, text=text)

    async def send_message(
        self, user_id: int, text: str, disable_notification: bool = False
    ) -> bool:
        try:
            await self.bot.send_message(
                user_id, text, disable_notification=disable_notification
            )
        except exceptions.TelegramNotFound:
            self.logger.exception(f"Target [ID:{user_id}]: failed")
        except Exception as exc:
            self.logger.error("", exc_info=exc)

        else:
            self.logger.info(f"Target [ID:{user_id}]: success")

            return True

        return False

    def prepare_message(self, message: types.Message) -> str:
        return json.dumps(
            {"answer": "answer later", "chat_id": message.chat.id}
        )
