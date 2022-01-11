from config import token
import requests
import datetime
from main import get_areas_list, get_area_universities, get_university_department
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text

bot = Bot(token=token)
dp = Dispatcher(bot)

areas_list = list(get_areas_list())


async def on_startup(_):
    print("Bot has been launched")


@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["/area",]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer("Let's start", reply_markup=keyboard)


@dp.message_handler(commands="area")
async def start(message: types.Message):
    area_buttons = get_areas_list()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*area_buttons)
    await message.answer("Loading...", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Choose your area", reply_markup=keyboard)


@dp.message_handler()
async def get_uni_data(message: types.Message):
    if message.text in areas_list:
        area_universities = get_area_universities(message.text)
        for k, v in sorted(area_universities.items()):
            university_data = f"{v}"
                            # f"{v['university_url']}"
            await message.answer(university_data, reply_markup=types.ReplyKeyboardRemove())


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
