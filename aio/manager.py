from core.config import config


class MessageManager:
    async def handle_updates(self, message_dict):
        config.logger.info("handle_updates %s", message_dict)
