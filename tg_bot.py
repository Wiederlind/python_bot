import asyncio
import aiohttp
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import CommandStart
from os import getenv

BOT_TOKEN = getenv("BOT_TOKEN")
CAT_API_KEY = getenv("CAT_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🦆"), KeyboardButton(text="🐈")]],
    resize_keyboard=True,
)


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Выбери кнопку ниже:", reply_markup=keyboard)


@dp.message(F.text.in_(["🦆", "🐈"]))
async def send_animal(message: types.Message):
    is_duck = message.text == "🦆"
    url, is_gif = await (get_duck_url() if is_duck else get_cat_url())

    if url:
        send = (
            message.answer_animation
            if is_gif or url.endswith(".gif")
            else message.answer_photo
        )
        await send(url, reply_markup=keyboard)
    else:
        await message.answer(
            f"Не удалось получить {message.text}", reply_markup=keyboard
        )


@dp.message()
async def fallback_handler(message: types.Message):
    await message.answer("Нажми на одну из кнопок ниже")


async def get_duck_url():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://random-d.uk/api/v2/random") as r:
                return (await r.json()).get("url"), False
    except:
        return None, False


async def get_cat_url():
    try:
        d_type = random.choice(["image/gif", "image/jpeg"])
        headers = {"x-api-key": CAT_API_KEY} if CAT_API_KEY else {}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.thecatapi.com/v1/images/search?mime_types={d_type}",
                headers=headers,
            ) as r:
                data = await r.json()
                return (
                    (data[0]["url"], d_type == "image/gif") if data else (None, False)
                )
    except:
        return None, False


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
