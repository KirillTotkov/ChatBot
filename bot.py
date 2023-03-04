import re
from enum import Enum

import openai
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import CantParseEntities

from settings import BOT_TOKEN, OPENAI_API_KEY, MODEL_NAME, BOT_HISTORY_LENGTH, BOT_ADMIN_ID, logger
from translator import translate_message_to_russian, translate_message_to_english

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
logger.info("Bot has started")
openai.api_key = OPENAI_API_KEY


def check_admin(func):
    async def wrapper(message: types.Message):
        if message.from_user.id != BOT_ADMIN_ID:
            return None
        await func(message)

    return wrapper


class Role(Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class MessageHistory:
    def __init__(self):
        self.history = []

    def add_message(self, role: Role, message):
        message = {"role": role.value, "content": message}
        self.history.append(message)

    def clear(self):
        self.history = []
        logger.info("Message History was cleared")

    def get_history(self, history_length=BOT_HISTORY_LENGTH):
        return self.history[-history_length:]


MESSAGE_HISTORY = MessageHistory()


class Form(StatesGroup):
    continue_chat = State()
    ready_to_end = State()


@dp.message_handler(commands=["start"])
@check_admin
async def welcome(message: types.Message):
    logger.info("/start command was invoked")
    await message.answer(
        "Привет! Я притворяюсь, что я ChatGPT :)\n" "Команды: /new_chat \n"
        "Если хотите чтобы ответ был переведен на русский перед сообщение напишите /ru"
    )


@dp.message_handler(commands=["new_chat"])
@check_admin
async def new_chat(message: types.Message):
    """Start a new chat, the previous history will be removed from the bot's memory"""
    logger.info("/new_chat command was invoked")
    MESSAGE_HISTORY.clear()
    start_message = "Привет! Я ваш собственный ChatGPT в Telegram :) Чем я могу вам помочь?"
    MESSAGE_HISTORY.add_message(Role.SYSTEM, start_message)
    await Form.continue_chat.set()
    await message.answer(start_message)


@dp.message_handler(state=Form.continue_chat)
async def continue_conversation(message: types.Message, state: FSMContext):
    """Continue conversation after the chat was started"""

    await state.finish()

    user_answer = message.text
    if user_answer.startswith('/ru'):
        user_answer = user_answer[3:]

    en_user_answer = translate_message_to_english(user_answer)

    if user_answer == "/new_chat":
        await new_chat(message)
        return

    MESSAGE_HISTORY.add_message(Role.USER, en_user_answer)

    try:
        gpt_response = await get_chatgpt_response(MESSAGE_HISTORY)
    except Exception as e:
        await message.answer(f"OpenAI Error: {e}")
        return

    if '/ru' in message.text:
        gpt_response = translate_message_to_russian(gpt_response)

    MESSAGE_HISTORY.add_message(Role.ASSISTANT, gpt_response)

    await Form.continue_chat.set()

    try:
        await message.answer(gpt_response, parse_mode=types.ParseMode.MARKDOWN)
    except CantParseEntities as e:
        await message.answer(f"Ошибка парсинга ответа \n {e}")


async def get_chatgpt_response(
        message_history: MessageHistory, history_length=BOT_HISTORY_LENGTH
) -> str:
    """
    Main function that communicates with the ChatGPT API
    """
    logger.info("Query GhatGPT API")
    response = await openai.ChatCompletion.acreate(
        model=MODEL_NAME,
        messages=message_history.get_history(history_length=history_length),
    )
    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
