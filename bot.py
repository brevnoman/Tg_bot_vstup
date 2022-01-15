from config import token
import requests
import datetime
from main import get_areas_dict, get_area_universities, get_university_department
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
import json
from models import engine, Session, Vstup

bot = Bot(token=token)
dp = Dispatcher(bot)


menu_cd = CallbackData("show_menu")

@dp.callback_query_handler(Text(startswith="dep_"))
async def get_speciality(call: types.CallbackQuery):
    dep_data_id = call["data"].replace('dep_', '')
    # specialities = session.query(Vstup).filter(Vstup.department == dep_data_id).distinct(Vstup.speciality).all()
    one_dep = session.query(Vstup).filter(Vstup.id == dep_data_id).first()
    specialities = session.query(Vstup).filter(Vstup.department == one_dep.department).distinct(Vstup.speciality).all()
    # print(one_dep.department)
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for speciality in specialities:
        buttons.append(types.InlineKeyboardButton(text=speciality.speciality,
                                                  url='youtube.com'))
    if len(buttons) > 10:
        keyboard.add(*buttons[0:10])
    else:
        keyboard.add(*buttons)
    await call.message.answer("Choose your speciality", reply_markup=keyboard)

@dp.callback_query_handler(Text(startswith="uni_"))
async def get_department(call: types.CallbackQuery):
    uni_data_url = call["data"].replace('uni_', '')
    departments = session.query(Vstup).filter(Vstup.university_url == uni_data_url).distinct(Vstup.department).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for department in departments:
        buttons.append(types.InlineKeyboardButton(text=department.department,
                                                  callback_data=f'dep_{department.id}'))
        # print(department.id)

    if len(buttons) > 10:
        keyboard.add(*buttons[0:10])
    else:
        keyboard.add(*buttons)
    await call.message.answer("Choose your department", reply_markup=keyboard)

@dp.callback_query_handler(Text(startswith="area_"))
async def get_universities(call: types.CallbackQuery):
    area_data_url = call["data"].replace('area_', '')
    universities = session.query(Vstup).filter(Vstup.area_url == area_data_url).distinct(Vstup.university_url).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for university in universities:
        buttons.append(types.InlineKeyboardButton(text=university.university,
                                                  callback_data=f'uni_{university.university_url}'))
    if len(buttons) > 10:
        keyboard.add(*buttons[0:10])
    else:
        keyboard.add(*buttons)
    await call.message.answer("Choose your department", reply_markup=keyboard)


@dp.message_handler(commands="start")
async def get_areas(message: types.Message):

    session = Session(bind=engine)
    area_dict = {}
    buttons = []
    data = session.query(Vstup).distinct(Vstup.area).all()
    for i in data:
        area_dict[i.area] = i.area_url
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for k, v_url in area_dict.items():
        button = types.InlineKeyboardButton(text=k, callback_data=f'area_{v_url}')
        buttons.append(button)
    keyboard.add(*buttons)
    await message.answer("Choose your area", reply_markup=keyboard)




session = Session(bind=engine)

async def on_startup(_):
    print("Bot has been launched")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
