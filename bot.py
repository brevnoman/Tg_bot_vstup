from config import token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from models import engine, Session, Vstup, UserSubjects

bot = Bot(token=token)
dp = Dispatcher(bot)

menu_cd = CallbackData("show_menu")

next_emoji = u"\u27A1"
previous_emoji = u'\u2b05'


@dp.callback_query_handler(Text(startswith="recalc_"))
async def recalc(call: types.CallbackQuery):
    speciality_id = call["data"].replace("recalc_", "")
    speciality = session.query(Vstup).filter(Vstup.id == speciality_id).first()
    user_subjects = session.query(UserSubjects).filter(UserSubjects.user_id == call["from"]["id"]).first()
    optionally_subjects = []
    need_subjects = []
    result_grade = 0
    for subject, coef in speciality.subjects.items():
        if subject.endswith('*'):
            optionally_subjects.append(coef)
        else:
            need_subjects.append(coef)
    counter = 0
    for subject in need_subjects:
        counter += 1
        subject_grade = eval(f"user_subjects.sub{counter}")
        result_grade += subject * subject_grade
    if optionally_subjects:
        counter+=1
        subject_grade = eval(f"user_subjects.sub{counter}")
        result_grade += optionally_subjects[0] * subject_grade
    if speciality.avg_grade_for_budget:
        if result_grade >= speciality.avg_grade_for_budget:
            await call.message.answer("You can pass budget")
        else:
            await call.message.answer("You can not pass budget")
    if speciality.avg_grade_for_contract:
        if result_grade >= speciality.avg_grade_for_contract:
            await call.message.answer("You can pass contract")
        else:
            await call.message.answer("You can not pass contract")
    if not speciality.avg_grade_for_budget and not speciality.avg_grade_for_contract:
        await call.message.answer("Net dannih")
    await call.message.answer(text=f"{result_grade}")


@dp.message_handler(Text(startswith="/sub"))
async def add_grade(message: types.Message):
    data = message["text"].replace("/sub", "").split()
    if len(data) < 2:
        await message.answer("You should write like this '/sub1 190'")
    else:
        if not data[0].isdecimal() or not data[1].isdecimal():
            await message.answer("It should be decimal")
        else:
            if 1 > int(data[0]) or int(data[0]) > 6 or 100 > int(data[1]) or int(data[1]) > 200:
                await message.answer("Wrong value")
            else:
                user_subjects = session.query(UserSubjects).filter_by(user_id=message["from"]["id"]).first()
                if not user_subjects:
                    user_subjects = UserSubjects(user_id=message["from"]["id"])
                    session.add(user_subjects)
                    session.commit()
                if data[0] == "1":
                    user_subjects.sub1 = data[1]
                if data[0] == "2":
                    user_subjects.sub2 = data[1]
                if data[0] == "3":
                    user_subjects.sub3 = data[1]
                if data[0] == "4":
                    user_subjects.sub4 = data[1]
                if data[0] == "5":
                    user_subjects.sub5 = data[1]
                if data[0] == "6":
                    user_subjects.sub6 = data[1]
                session.commit()


@dp.callback_query_handler(Text(startswith="spec_"))
async def get_data_subjects(call: types.CallbackQuery):
    call_data = call["data"].replace('spec_', '')
    data = session.query(Vstup).filter(Vstup.id == call_data).first()
    user_subjects = session.query(UserSubjects).filter_by(user_id=call["from"]["id"]).first()
    if not user_subjects:
        user_subjects = UserSubjects(user_id=call["from"]["id"])
        session.add(user_subjects)
        session.commit()
    buttons = []
    # mb nado budet
    need_subjects = []
    optionally_subjects = []

    for subject, coef in data.subjects.items():
        if subject.endswith('*'):
            optionally_subjects.append(subject)
        else:
            need_subjects.append(subject)
    need_subjects_string = ""
    optionally_subjects_string = ""
    counter = 0
    for n in need_subjects:
        counter += 1
        need_subjects_string += f"/sub{counter} for {n}\n"
    if optionally_subjects:
        optionally_subjects_string += f"/sub{counter+1} for"
    for o in optionally_subjects:
        optionally_subjects_string += f" {o},"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_return = types.InlineKeyboardButton(text="Return"+u"\u274C", callback_data=f'dep_{data.id}-0')
    buttons.append(button_return)
    button_reculc = types.InlineKeyboardButton(text="Recalc", callback_data=f'recalc_{data.id}')
    buttons.append(button_reculc)
    keyboard.add(*buttons)
    await call.message.edit_text(f'Введите следующие предметы как указано в примере\n'
                                 f'Пример "/sub1 190"\n'
                                 f'{need_subjects_string}'
                                 f'{optionally_subjects_string}\n'
                                 f'When you will enter all grades press Recalc button'
                                 )
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="dep_"))
async def get_speciality(call: types.CallbackQuery):
    dep_data_id = call["data"].replace('dep_', '').split("-")
    id = dep_data_id[0]
    first = int(dep_data_id[1])
    user_subs = session.query(UserSubjects).filter(UserSubjects.user_id == call["from"]["id"]).first()
    user_subs.set_default()
    session.commit()
    one_dep = session.query(Vstup).filter(Vstup.id == id).first()
    specialities = session.query(Vstup).filter(Vstup.depends_on == one_dep.depends_on).filter(Vstup.study_degree == one_dep.study_degree).filter(Vstup.university_url == one_dep.university_url).filter(Vstup.department == one_dep.department).distinct(Vstup.speciality).all()
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
    button = types.InlineKeyboardButton(text="Return"+u"\u274C", callback_data=f'uni_{id}-0')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose speciality')
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="uni_"))
async def get_department(call: types.CallbackQuery):
    uni_data_url = call["data"].replace('uni_', '').split("-")
    id = uni_data_url[0]
    print(id)
    one_uni = session.query(Vstup).filter(Vstup.id == id).first()
    first = int(uni_data_url[1])
    departments = session.query(Vstup).filter(Vstup.university_url == one_uni.university_url).filter(Vstup.study_degree == one_uni.study_degree).filter(Vstup.depends_on == one_uni.depends_on).distinct(Vstup.department).all()
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
                                                     callback_data=f'uni_{id}-{last}'))
    if first:
        buttons.append(types.InlineKeyboardButton(text="Previous"+previous_emoji,
                                                 callback_data=f'uni_{id}-{first-10}'))
    button = types.InlineKeyboardButton(text="Return"+u"\u274C", callback_data=f'area_{departments[0].id}-0')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose department')
    await call.message.edit_reply_markup(keyboard)



@dp.callback_query_handler(Text(startswith="area_"))
async def get_universities(call: types.CallbackQuery):
    area_data_url = call["data"].replace('area_', '').split("-")
    url = area_data_url[0]
    first = int(area_data_url[1])
    one_area = session.query(Vstup).filter(Vstup.id == url).first()
    universities = session.query(Vstup).filter(Vstup.area_url == one_area.area_url).filter(Vstup.study_degree == one_area.study_degree).filter(Vstup.depends_on == one_area.depends_on).distinct(Vstup.university_url).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    if len(universities) <= first + 10:
        last = len(universities)
    else:
        last = first + 10
    for university in range(first, last):
        buttons.append(types.InlineKeyboardButton(text=universities[university].university,
                                                  callback_data=f'uni_{universities[university].id}-0'))
    if first:
        buttons.append(types.InlineKeyboardButton(text=f"Previous "+previous_emoji,
                                                  callback_data=f'area_{url}-{first-10}'))
    if last != len(universities):
        buttons.append(types.InlineKeyboardButton(text="Next "+next_emoji,
                                                  callback_data=f'area_{url}-{last}'))
    button = types.InlineKeyboardButton(text="Return"+u"\u274C", callback_data=f'depends_{universities[0].id}')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose university')
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="depends_"))
async def get_areas(call: types.CallbackQuery):
    session = Session(bind=engine)
    buttons = []
    data_call = call["data"].replace('depends_', '')
    one_depend = session.query(Vstup).filter(Vstup.id == data_call).first()
    data = session.query(Vstup).filter(Vstup.study_degree == one_depend.study_degree).filter(Vstup.depends_on == one_depend.depends_on).distinct(Vstup.area).all()
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for i in data:
        button = types.InlineKeyboardButton(text=i.area, callback_data=f'area_{i.id}-0')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return"+u"\u274C", callback_data=f'degree_{data_call}')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose area')
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
    button = types.InlineKeyboardButton(text="Return"+u"\u274C", callback_data=f'start_')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose qualification')
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