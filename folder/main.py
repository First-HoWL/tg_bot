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

def check_game(field):
    """
    'X'  - победил X
    'O'  - победил O
    'draw' - ничья
    None - игра продолжается
    """

    lines = []

    lines.extend(field)

    for col in range(3):
        lines.append([field[row][col] for row in range(3)])

    lines.append([field[i][i] for i in range(3)])
    lines.append([field[i][2 - i] for i in range(3)])

    for line in lines:
        if line == ["X", "X", "X"]:
            return "X"
        if line == ["O", "O", "O"]:
            return "O"

    if all(cell != "" for row in field for cell in row):
        return "draw"

    return None

def validate_move(field, row, col):
    
    if not (0 <= row < 3 and 0 <= col < 3):
        return False

    if field[row][col] != "":
        return False

    return True


# Обробник команди /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Let`s talk!")

@dp.message(Command("startBotGame"))
async def botGame(message: Message):
    field = {{"","",""},{"","",""},{"","",""}}
    current_player = "X"
    while True:
        if check_game(field) is None:
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=str(field) + f"ты играешь за {current_player}",
                    config=types.GenerateContentConfig(
                        system_instruction="""
                        Ты — игрок в крестики нолики, у тебя есть поле и твой знак, ты должен победить, не жульничай.
                        В ответ возвращай в таком формате(y,x): 2,3 без других символов
                        """,
                    )
                )
            except Exception as err:
                print(f"{type(err)}: {err}")
                await message.answer("Щось пішло не так")
            else:
                # await message.answer(str())
                if validate_move(field, response.text.strip(',')[0], response.text.strip(',')[1]):
                    field[response.text.strip(',')[0]][response.text.strip(',')[1]] = current_player
                    await message.answer(
                        f"-------------\n" \
                        f"| {field[0][0]} | {field[0][1]} | {field[0][2]} |\n" \
                        f"-------------\n" \
                        f"| {field[1][0]} | {field[1][1]} | {field[1][2]} |\n" \
                        f"-------------\n" \
                        f"| {field[2][0]} | {field[2][1]} | {field[2][2]} |\n" \
                        f"-------------")
        else:
            win = check_game(field)
            if win == "X":
                await message.answer("X win!")
            elif win == "O":
                await message.answer("O win!")
            elif win == "draw":
                await message.answer("Draw!")
            break

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