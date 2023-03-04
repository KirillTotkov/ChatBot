import os
import logging

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("gpt_chat")
logger.setLevel("INFO")

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_ADMIN_ID = int(os.getenv("BOT_ADMIN_ID"))

MODEL_NAME = "gpt-3.5-turbo"

BOT_HISTORY_LENGTH = 20
