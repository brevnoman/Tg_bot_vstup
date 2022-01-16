from config import token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from models import engine, Session, Vstup

bot = Bot(token=token)
dp = Dispatcher(bot)

menu_cd = CallbackData("show_menu")


@dp.callback_query_handler(Text(startswith="dep_"))
async def get_speciality(call: types.CallbackQuery):
    dep_data_id = call["data"].replace('dep_', '').split("-")
    id = dep_data_id[0]
    first = int(dep_data_id[1])
    next_emoji = u"\u27A1"
    previous_emoji = u'\u2b05'
    one_dep = session.query(Vstup).filter(Vstup.id == id).first()
    specialities = session.query(Vstup).filter(Vstup.department == one_dep.department).distinct(Vstup.speciality).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if len(specialities) <= first + 10:
        last = len(specialities)
    else:
        last = first + 10
    for speciality in range(first, last):
        buttons.append(types.InlineKeyboardButton(text=specialities[speciality].speciality,
                                                  callback_data=f'spec_{specialities[speciality].id}'))
    if last != len(specialities):
        buttons.append(types.InlineKeyboardButton(text="Next"+next_emoji,
                                                     callback_data=f'dep_{id}-{last}'))
    if first:
        buttons.append(types.InlineKeyboardButton(text="Previous"+previous_emoji,
                                                 callback_data=f'dep_{id}-{first-10}'))
    button = types.InlineKeyboardButton(text="Vernutsa nazad"+u"\u274C", callback_data=f'uni_{specialities[0].university_url}-0')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="uni_"))
async def get_department(call: types.CallbackQuery):
    uni_data_url = call["data"].replace('uni_', '').split("-")
    url = uni_data_url[0]
    first = int(uni_data_url[1])
    next_emoji = u"\u27A1"
    previous_emoji = u'\u2b05'
    departments = session.query(Vstup).filter(Vstup.university_url == url).distinct(Vstup.department).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if len(departments) <= first + 10:
        last = len(departments)
    else:
        last = first + 10
    for department in range(first, last):
        buttons.append(types.InlineKeyboardButton(text=departments[department].department,
                                                  callback_data=f'dep_{departments[department].id}-0'))
    if last != len(departments):
        buttons.append(types.InlineKeyboardButton(text="Next"+next_emoji,
                                                     callback_data=f'uni_{url}-{last}'))
    if first:
        buttons.append(types.InlineKeyboardButton(text="Previous"+previous_emoji,
                                                 callback_data=f'uni_{url}-{first-10}'))
    button = types.InlineKeyboardButton(text="Vernutsa nazad"+u"\u274C", callback_data=f'area_{departments[0].area_url}-0')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)



@dp.callback_query_handler(Text(startswith="area_"))
async def get_universities(call: types.CallbackQuery):
    area_data_url = call["data"].replace('area_', '').split("-")
    url = area_data_url[0]
    first = int(area_data_url[1])
    universities = session.query(Vstup).filter(Vstup.area_url == url).distinct(Vstup.university_url).all()
    buttons = []
    next_emoji = u"\u27A1"
    previous_emoji = u'\u2b05'
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if len(universities) <= first + 10:
        last = len(universities)
    else:
        last = first + 10
    for university in range(first, last):
        buttons.append(types.InlineKeyboardButton(text=universities[university].university,
                                                  callback_data=f'uni_{universities[university].university_url}-0'))
    if first:
        buttons.append(types.InlineKeyboardButton(text=f"Previous "+previous_emoji,
                                                  callback_data=f'area_{url}-{first-10}'))
    if last != len(universities):
        buttons.append(types.InlineKeyboardButton(text="Next "+next_emoji,
                                                  callback_data=f'area_{url}-{last}'))
    button = types.InlineKeyboardButton(text="Vernutsa nazad"+u"\u274C", callback_data=f'depends_{universities[0].id}')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="depends_"))
async def get_areas(call: types.CallbackQuery):
    session = Session(bind=engine)
    buttons = []
    data_call = call["data"].replace('depends_', '')
    one_depend = session.query(Vstup).filter(Vstup.id == data_call).first()
    data = session.query(Vstup).filter(Vstup.depends_on == one_depend.depends_on).distinct(Vstup.area).all()
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for i in data:
        button = types.InlineKeyboardButton(text=i.area, callback_data=f'area_{i.area_url}-0')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Vernutsa nazad"+u"\u274C", callback_data=f'degree_{data_call}')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="degree_"))
async def get_depends_on(call: types.CallbackQuery):
    data = call["data"].replace('degree_', '')
    buttons = []
    one_degree = session.query(Vstup).filter(Vstup.id == data).first()
    depends_data = session.query(Vstup).filter(Vstup.study_degree == one_degree.study_degree) \
        .distinct(Vstup.depends_on).all()
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for i in depends_data:
        button = types.InlineKeyboardButton(text=i.depends_on, callback_data=f'depends_{i.id}')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Vernutsa nazad"+u"\u274C", callback_data=f'start_')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_reply_markup(keyboard)


@dp.message_handler(commands="start")
@dp.callback_query_handler(Text(startswith="start_"))
async def get_degree(message: types.Message):
    session = Session(bind=engine)
    buttons = []
    data = session.query(Vstup).distinct(Vstup.study_degree).all()
    for i in data:
        button = types.InlineKeyboardButton(text=i.study_degree, callback_data=f'degree_{i.id}')
        buttons.append(button)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    if isinstance(message, types.CallbackQuery):
        await message.message.edit_reply_markup(keyboard)
    else:
        await message.answer("Zdarov, vibiray", reply_markup=keyboard)


session = Session(bind=engine)


async def on_startup(_):
    print("Bot has been launched")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
