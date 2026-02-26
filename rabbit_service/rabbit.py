import json

import aio_pika
import pamqp
from aio_pika.abc import (
    AbstractChannel,
    AbstractQueue,
    AbstractRobustConnection,
)

from aio.manager import MessageManager
from core.config import config


class QueueAccessor:
    def __init__(self, message_manager):
        self.config = config
        self.logger = config.logger
        self.message_manager: MessageManager = message_manager
        self.username = config.rabbit.user
        self.password = str(config.rabbit.password)
        self.host = config.rabbit.host
        self.queue_title = config.rabbit.queue_title
        self.port = 5672
        self.async_connection: AbstractRobustConnection | None = None
        self.async_channel: AbstractChannel | None = None

    async def connect(self) -> None:
        if not self.async_connection or self.async_connection.is_closed:
            self.async_connection = await aio_pika.connect_robust(
                host=self.host,
                login=self.username,
                password=self.password,
                port=self.port,
            )

        if not self.async_channel or self.async_channel.is_closed:
            self.async_channel = await self.async_connection.channel()

        await self.async_channel.declare_queue(self.queue_title, durable=True)

    async def disconnect(self) -> None:
        if self.async_channel:
            await self.async_channel.close()

        if self.async_connection:
            await self.async_connection.close()

    async def send_to_queue(self, message: str) -> None:
        await self.connect()

        await self.async_channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
            ),
            routing_key=self.queue_title,
        )
        self.logger.info("Sent to queue %s", message)

    async def process_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        message_dict = {}
        content_type = (
            message.headers.get("content_type") or message.content_type
        )

        try:
            async with message.process(ignore_processed=True):
                if content_type == "application/json":
                    try:
                        message_dict = json.loads(message.body.decode("utf-8"))
                    except json.JSONDecodeError:
                        self.logger.warning(f"Invalid JSON: {message.body}")
                        await message.nack(requeue=False)
                        return
                else:
                    self.logger.warning(f"Invalid JSON: {message.body}")
                    await message.nack(requeue=False)
                    return

                await self.message_manager.handle_updates(message_dict)
                await message.ack()
                self.logger.info("Message consumed")
        except Exception as exc:
            self.logger.error(
                f"Error processing message {message}: ", exc_info=exc
            )
            await message.nack(requeue=False)

    async def receive_from_queue(self) -> None:
        await self.connect()

        await self.async_channel.set_qos(prefetch_count=1)
        queue: AbstractQueue = await self.async_channel.declare_queue(
            self.queue_title, durable=True, auto_delete=False
        )

        try:
            await queue.consume(callback=self.process_message, no_ack=False)
        except (pamqp.exceptions.AMQPFrameError, KeyboardInterrupt):
            await self.async_connection.close()
            self.logger.warning("QueueAccessor closed async_connection")
