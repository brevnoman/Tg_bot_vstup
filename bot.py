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
    one_dep = session.query(Vstup).filter(Vstup.id == dep_data_id).first()
    specialities = session.query(Vstup).filter(Vstup.department == one_dep.department).distinct(Vstup.speciality).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for speciality in specialities:
        buttons.append(types.InlineKeyboardButton(text=speciality.speciality,
                                                  url='youtube.com'))
    if len(buttons) > 10:
        keyboard.add(*buttons[0:10])
    else:
        keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="uni_"))
async def get_department(call: types.CallbackQuery):
    uni_data_url = call["data"].replace('uni_', '')
    departments = session.query(Vstup).filter(Vstup.university_url == uni_data_url).distinct(Vstup.department).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for department in departments:
        buttons.append(types.InlineKeyboardButton(text=department.department,
                                                  callback_data=f'dep_{department.id}'))

    if len(buttons) > 10:
        keyboard.add(*buttons[0:10])
    else:
        keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


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
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="depends_"))
async def get_areas(call: types.CallbackQuery):

    session = Session(bind=engine)
    area_dict = {}
    buttons = []
    data_call = call["data"].replace('depends_', '')
    one_depend = session.query(Vstup).filter(Vstup.id == data_call).first()
    data = session.query(Vstup).filter(Vstup.depends_on == one_depend.depends_on).distinct(Vstup.area).all()
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for i in data:
        button = types.InlineKeyboardButton(text=i.area, callback_data=f'area_{i.area_url}')
        buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="degree_"))
async def get_depends_on(call: types.CallbackQuery):

    data = call["data"].replace('degree_', '')
    buttons = []
    one_degree = session.query(Vstup).filter(Vstup.id == data).first()
    depends_data = session.query(Vstup).filter(Vstup.study_degree == one_degree.study_degree)\
        .distinct(Vstup.depends_on).all()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for i in depends_data:
        button = types.InlineKeyboardButton(text=i.depends_on, callback_data=f'depends_{i.id}')
        buttons.append(button)
    keyboard.add(*buttons)
    # await call.message.edit_text("Choooooseee")
    await call.message.edit_reply_markup(keyboard)

@dp.message_handler(commands="start")
async def get_degree(message: types.Message):

    session = Session(bind=engine)
    buttons = []
    data = session.query(Vstup).distinct(Vstup.study_degree).all()
    for i in data:
        button = types.InlineKeyboardButton(text=i.study_degree, callback_data=f'degree_{i.id}')
        buttons.append(button)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    await message.answer("Hello! Choose your degree", reply_markup=keyboard)



session = Session(bind=engine)

async def on_startup(_):
    print("Bot has been launched")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)