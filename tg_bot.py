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


def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🦆"),
                KeyboardButton(text="🐈"),
            ]
        ],
        resize_keyboard=True,
    )


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Выбери кнопку ниже:", reply_markup=get_main_keyboard())


@dp.message(F.text == "🦆")
async def send_duck(message: types.Message):
    url = await get_duck_url()
    if url:
        if url.endswith(".gif"):
            await message.answer_animation(
                animation=url, reply_markup=get_main_keyboard()
            )
        else:
            await message.answer_photo(photo=url, reply_markup=get_main_keyboard())
    else:
        await message.answer("Не удалось получить 🦆", reply_markup=get_main_keyboard())


@dp.message(F.text == "🐈")
async def send_cat(message: types.Message):
    url, is_gif = await get_cat_url()
    if url:
        if is_gif:
            await message.answer_animation(
                animation=url, reply_markup=get_main_keyboard()
            )
        else:
            await message.answer_photo(photo=url, reply_markup=get_main_keyboard())
    else:
        await message.answer("Не удалось получить 🐈", reply_markup=get_main_keyboard())


async def get_duck_url():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://random-d.uk/api/random") as response:
                data = await response.json()
                return data.get("url")
    except:
        return None


async def get_cat_url():
    try:
        cat_type = random.choice(["image/gif", "image/jpeg"])
        headers = {}
        if CAT_API_KEY:
            headers["x-api-key"] = CAT_API_KEY

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.thecatapi.com/v1/images/search?mime_types={cat_type}",
                headers=headers,
            ) as response:
                data = await response.json()
                if data and "url" in data[0]:
                    return data[0]["url"], cat_type == "image/gif"
    except:
        return None, False
    return None, False


async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
