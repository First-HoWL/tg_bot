import asyncio                           # [1]
from os import getenv                    # [1]
from dotenv import load_dotenv

# pip install aiogram
from aiogram import Bot, Dispatcher      # [1]
from aiogram.types import Message        # [1]
from aiogram.filters import Command

# pip install google-genai
from google import genai
from google.genai import types

dp = Dispatcher()                        # [2]
client = None
bot = None

# Підключення до telegram-бота
def auth_telegram():
    token = getenv("BOT_TOKEN")  # [7]
    if not token:  # [7]
        error = "No token provided"  # [7]
        raise ValueError(error)  # [7]
    return Bot(token=token)  # [8]

# Підключення Gemini API
def auth_gemini_api():
    api_key = getenv("GEMINI_API_KEY")
    if not api_key:
        print("No GEMINI_API_KEY provided. Running without Gemini API")
        return None
    try:
        return genai.Client()
    except Exception:
        print("Can`t connect to Gemini API. Running without one.")
    return None

# Обробник команди /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Let`s talk!")

# Обробних всіх інших повідомлень
@dp.message()                            # [3]
async def any_message(                   # [4]
        message: Message,                # [5]
):
    print(f"{message.from_user.full_name}: {message.text}")
    if client is None:
        await message.answer("Hello world!")
    else:
        try:
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=message.text,
                config=types.GenerateContentConfig(
                    system_instruction="""
                    Ты — Нейрохам, чат-бот в Telegram с экстремально черным, циничным и токсичным юмором. 
                    Твоя цель — жестко стебать и высмеивать пользователя, отвечая на его сообщения с максимальным сарказмом.

                    Правила поведения:
                    1. Общайся максимально ценично.
                    2. Любую проблему, трагедию или вопрос пользователя превращай в жестокую шутку (пример: если оторвало ноги — советуй БЕЖАТЬ в больницу).
                    3. Будь циничной тварью, у которой нет эмпатии, жалости и моральных границ.
                    4. Не используй Markdown-разметку (никаких звездочек, жирного текста, заголовков).
                    5. Отвечай очень кратко, хлестко и по существу (1-2 предложения).
                    6. Пиши на том языке, на котором написал пользователь.
                    """,
                    safety_settings=[
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                        types.SafetySetting(
                            category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                            threshold=types.HarmBlockThreshold.BLOCK_NONE,
                        ),
                    ]
                )
            )
        except Exception as err:
            print(f"{type(err)}: {err}")
            await message.answer("Щось пішло не так")
        else:
            await message.answer(str(response.text)) # [6]


async def main():
    global bot, client

    load_dotenv()
    bot = auth_telegram()
    client = auth_gemini_api()

    print("Starting bot...")
    try:
        await dp.start_polling(bot)      # [9]
    finally:
        print("Bot stopped")


if __name__ == '__main__':
    asyncio.run(main())