import asyncio
import json
import typing
from dataclasses import asdict

import aio_pika
import pamqp
import pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractQueue,
    AbstractRobustConnection,
)

from core.config import config


class MessageManager:
    async def handle_updates(self, message_dict):
        config.logger.info("handle_updates %s", message_dict)


message_manager = MessageManager()


class QueueAccessor:
    def __init__(self):
        self.config = config
        self.logger = config.logger
        self.message_manager = message_manager
        self.username = config.rabbit.user
        self.password = str(config.rabbit.password)
        self.host = config.rabbit.host
        self.queue_title = config.rabbit.queue_title
        self.port = 5672
        self.sync_connection: pika.BlockingConnection | None = None
        self.async_connection: AbstractRobustConnection | None = None
        self.async_channel: AbstractChannel | None = None

    async def connect(self) -> None:
        if not self.sync_connection or self.sync_connection.is_closed:
            credentials = pika.PlainCredentials(
                username=self.username, password=self.password
            )
            parameters = pika.ConnectionParameters(
                host=self.host, credentials=credentials, port=self.port
            )
            self.sync_connection = pika.BlockingConnection(parameters)

        if not self.async_connection or self.async_connection.is_closed:
            self.async_connection = await aio_pika.connect_robust(
                host=self.host,
                login=self.username,
                password=self.password,
                port=self.port,
            )

    async def disconnect(self) -> None:
        if self.async_channel:
            await self.async_channel.close()

        if self.sync_connection:
            self.sync_connection.close()

        if self.async_connection:
            await self.async_connection.close()

    async def send_to_queue(self, bunch: list) -> None:
        await self.connect()
        channel = self.sync_connection.channel()
        channel.queue_declare(queue=self.queue_title, durable=True)
        for item in bunch:
            message = json.dumps(asdict(item))
            channel.basic_publish(
                exchange="",
                routing_key=self.queue_title,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                ),
            )
            self.logger.info("Sent to queue %s", message)
        channel.close()

    async def process_message(
        self, message: aio_pika.abc.AbstractIncomingMessage
    ) -> None:
        try:
            async with message.process(ignore_processed=True):
                message_dict = json.loads(message.body.decode("utf-8"))
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
        if not self.async_channel or self.async_channel.is_closed:
            self.async_channel = await self.async_connection.channel()
        await self.async_channel.set_qos(prefetch_count=1)
        queue: AbstractQueue = await self.async_channel.declare_queue(
            self.queue_title, durable=True, auto_delete=False
        )
        try:
            await queue.consume(callback=self.process_message, no_ack=False)
        except (pamqp.exceptions.AMQPFrameError, KeyboardInterrupt):
            await self.async_connection.close()
            self.logger.info("QueueAccessor closed async_connection")
