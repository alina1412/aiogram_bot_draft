from aiogram import types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from aio.manager import MessageManager
from aio.settings import dp
from aio.utils import MyCallback, get_from_tg_table, get_inline_keyboard
from core.config import config
from rabbit_service.rabbit import QueueAccessor


@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Hello! Send me any message.")


@dp.message(Command("later"))
async def start_command(
    message: types.Message,
    manager: MessageManager,
    queue_accessor: QueueAccessor,
):
    message = manager.prepare_message(message)
    await queue_accessor.send_to_queue(message)


@dp.message()
async def echo_handler(
    message: types.Message,
    session: AsyncSession,
) -> None:
    res = await get_from_tg_table(session)

    try:
        if message.text == "key":
            keyboard = get_inline_keyboard()
            await message.answer(
                f"You said: {message.text}", reply_markup=keyboard
            )
        else:
            await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("not all the types are supported")


@dp.callback_query(MyCallback.filter())
async def handle_callback(
    query: types.CallbackQuery, callback_data: MyCallback
):
    if callback_data.action == "button1":
        await query.message.answer("You pressed Button 1!")
    elif callback_data.action == "button2":
        await query.message.answer("You pressed Button 2!")
    await query.answer()
