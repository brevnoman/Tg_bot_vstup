from config import token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from models import engine, Vstup, UserSubjects
from sqlalchemy.orm import Session

bot = Bot(token=token)
dp = Dispatcher(bot)
session = Session(bind=engine)

next_emoji = u"\u27A1"
previous_emoji = u'\u2b05'


@dp.callback_query_handler(Text(startswith="recalc_"))
async def recalc(call: types.CallbackQuery):
    """
    Function calculating possibility to get on budget or contract
    speciality_id: id taken from call data mean id speciality object
    speciality: Vstup object that contain information of chosen speciality
    user_subjects: UserSubjects object that contain information about user id and subjects that user get specify
    optional_subjects: only one of given subjects needed
    need_subjects: every of given subjects need
    result_grade: grade based on user grades and coefficients for each of them
    """
    speciality_id = call["data"].replace("recalc_", "")
    speciality = session.query(Vstup).filter(Vstup.id == speciality_id).first()
    user_subjects = await set_user_subs(call)
    optionally_subjects, need_subjects = await get_subjects_lists(data=speciality)
    result_grade = 0
    counter = 0
    for subject in need_subjects:
        counter += 1
        subject_grade = user_subjects.get_subject_by_counter(counter=counter)
        result_grade += subject[1] * subject_grade
    if optionally_subjects:
        counter += 1
        subject_grade = user_subjects.get_subject_by_counter(counter=counter)
        result_grade += optionally_subjects[0][1] * subject_grade
    if speciality.avg_grade_for_budget:
        await message_of_pass(result_grade=result_grade,
                              previous_year_grade=speciality.avg_grade_for_budget,
                              call=call,
                              type_of_edu="budget")
    if speciality.avg_grade_for_contract:
        await message_of_pass(result_grade=result_grade,
                              previous_year_grade=speciality.avg_grade_for_contract,
                              call=call,
                              type_of_edu="contract")
    if not speciality.avg_grade_for_budget and not speciality.avg_grade_for_contract:
        await call.message.answer("We have no data about previous years contract or budget average grade(")
    await call.message.answer(text=f"Your average grade is {result_grade}")


async def message_of_pass(result_grade, previous_year_grade, call, type_of_edu):
    if result_grade >= previous_year_grade:
        await call.message.answer(f"You can pass {type_of_edu}")
    else:
        await call.message.answer(f"You can not pass {type_of_edu}")


@dp.message_handler(Text(startswith="/sub"))
async def add_grade(message: types.Message):
    """
    Handler that give possibility to specify subjects degree
    data: list that contains information about counter of subject and it's grade
    user_subjects: UserSubjects object that contain information about user id and subjects that user get specify
    """
    data = message["text"].replace("/sub", "").split()
    if len(data) < 2:
        await message.answer("You should write like this '/sub1 190'")
    else:
        subject_number = data[0]
        subject_grade = data[1]
        if not subject_number.isdecimal() or not subject_grade.isdecimal():
            await message.answer("It should be decimal")
        else:
            if 1 > int(subject_number) or int(subject_number) > 6 or 100 > int(subject_grade) or int(
                    subject_grade) > 200:
                await message.answer("Wrong value")
            else:
                user_subjects = await set_user_subs(message)
                user_subjects.set_subject_by_counter(counter=int(subject_number), value=subject_grade)
                session.commit()


@dp.callback_query_handler(Text(startswith="spec_"))
async def get_data_subjects(call: types.CallbackQuery):
    """
    Gives information about subjects and how to specify it
    speciality_id: string contain id of Vstup object
    data: Vstup object contain information about chosen speciality
    buttons: list contains InlineKeyboardButton objects
    optional_subjects: only one of given subjects needed
    need_subjects: every of given subjects need
    need_subjects_string: string used to change message text to give information about needed subjects
    optionally_subjects_string: string used to list all optional subjects in text of message
    keyboard: InlineKeyboardMarkup object used to change keyboard of message
    """
    speciality_id = call["data"].replace('spec_', '')
    data = session.query(Vstup).filter(Vstup.id == speciality_id).first()
    buttons = []
    optionally_subjects, need_subjects = await get_subjects_lists(data)
    need_subjects_string = ""
    optionally_subjects_string = ""
    counter = 0
    for n in need_subjects:
        counter += 1
        need_subjects_string += f"/sub{counter} for {n[0]}\n"
    if optionally_subjects:
        optionally_subjects_string += f"/sub{counter + 1} for"
    for o in optionally_subjects:
        optionally_subjects_string += f" {o[0]},"
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_return = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'dep_{data.id}-0')
    buttons.append(button_return)
    button_calculate = types.InlineKeyboardButton(text="Calculate", callback_data=f'recalc_{data.id}')
    buttons.append(button_calculate)
    keyboard.add(*buttons)
    await call.message.edit_text(f'Enter next subjects as in example\n'
                                 f'Example "/sub1 190"\n'
                                 f'{need_subjects_string}'
                                 f'{optionally_subjects_string}\n'
                                 f'When you will enter all grades press Calculate button'
                                 )
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="dep_"))
async def get_speciality(call: types.CallbackQuery):
    """
    Function to get buttons with specialities of chosen department based on study degree and qualification
    dep_data: list contains id of Vstup object that have needed information
     and first object in row(used to make pagination)
    user_subs: UserSubjects object that contain information about user id and subjects that user get specify
    one_dep: Vstup objects that contains all needed information like chosen qualification, study degree and university
    specialities: list of Vstup objects that fit chosen criteria with unique specialities
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change keyboard of message
    last: used to make 10 buttons row just bigger than first by 10 or less
    """
    dep_data = call["data"].replace('dep_', '').split("-")
    department_id = dep_data[0]
    first = int(dep_data[1])
    user_subs = await set_user_subs(call)
    user_subs.set_default()
    session.commit()
    one_dep = session.query(Vstup).filter(Vstup.id == department_id).first()
    specialities = session.query(Vstup).filter(Vstup.depends_on == one_dep.depends_on).filter(
        Vstup.study_degree == one_dep.study_degree).filter(Vstup.university_url == one_dep.university_url).filter(
        Vstup.department == one_dep.department).distinct(Vstup.speciality).all()
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
        buttons.append(types.InlineKeyboardButton(text="Next" + next_emoji,
                                                  callback_data=f'dep_{department_id}-{last}'))
    if first:
        buttons.append(types.InlineKeyboardButton(text="Previous" + previous_emoji,
                                                  callback_data=f'dep_{department_id}-{first - 10}'))
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'uni_{department_id}-0')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose speciality')
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="uni_"))
async def get_department(call: types.CallbackQuery):
    """
    Function to get all departments for chosen university based on study degree and qualification
    uni_data: list contains first object in row and
     id of Vstup object that contain information about university, study degree and qualification
    one_uni: Vstup object that contain information about university, study degree and qualification
    departments: list of Vstup objects that fit to chosen criteria with unique departments
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change keyboard of message
    last: used to make 10 buttons row just bigger than first by 10 or less
    """
    uni_data = call["data"].replace('uni_', '').split("-")
    university_id = uni_data[0]
    one_uni = session.query(Vstup).filter(Vstup.id == university_id).first()
    first = int(uni_data[1])
    departments = session.query(
        Vstup).filter(
        Vstup.university_url == one_uni.university_url).filter(
        Vstup.study_degree == one_uni.study_degree).filter(
        Vstup.depends_on == one_uni.depends_on).distinct(
        Vstup.department).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    last = await get_last(objects=departments, first=first)
    for department in range(first, last):
        buttons.append(types.InlineKeyboardButton(text=departments[department].department,
                                                  callback_data=f'dep_{departments[department].id}-0'))
    if first:
        buttons.append(types.InlineKeyboardButton(text="Previous" + previous_emoji,
                                                  callback_data=f'uni_{university_id}-{first - 10}'))
    if last != len(departments):
        buttons.append(types.InlineKeyboardButton(text="Next" + next_emoji,
                                                  callback_data=f'uni_{university_id}-{last}'))
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'area_{departments[0].id}-0')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose department')
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="area_"))
async def get_universities(call: types.CallbackQuery):
    """
    Function to get universities based on area, study degree and qualification
    area_data: list contains index of first object in row and
     id of Vstup object that contain information about area, study degree and qualification
    one_area: Vstup object  that contain information about area, study degree and qualification
    universities: list of Vstup objects that fit to chosen criteria with unique universities
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change keyboard of message
    last: used to make 10 buttons row just bigger than first by 10 or less
    """
    area_data = call["data"].replace('area_', '').split("-")
    area_id = area_data[0]
    first = int(area_data[1])
    one_area = session.query(Vstup).filter(Vstup.id == area_id).first()
    universities = session.query(
        Vstup).filter(
        Vstup.area_url == one_area.area_url).filter(
        Vstup.study_degree == one_area.study_degree).filter(
        Vstup.depends_on == one_area.depends_on).distinct(
        Vstup.university_url).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    last = await get_last(objects=universities, first=first)
    for university in range(first, last):
        buttons.append(types.InlineKeyboardButton(text=universities[university].university,
                                                  callback_data=f'uni_{universities[university].id}-0'))
    if first:
        buttons.append(types.InlineKeyboardButton(text=f"Previous " + previous_emoji,
                                                  callback_data=f'area_{area_id}-{first - 10}'))
    if last != len(universities):
        buttons.append(types.InlineKeyboardButton(text="Next " + next_emoji,
                                                  callback_data=f'area_{area_id}-{last}'))
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'depends_{universities[0].id}')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose university')
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="depends_"))
async def get_areas(call: types.CallbackQuery):
    """
    Function to get areas based on study degree and qualification
    depends_id: id of Vstup object that contain information about study degree and qualification
    one_depend: Vstup object that contain information about study degree and qualification
    areas: list of Vstup objects that fit to chosen criteria with unique areas
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change keyboard of message
    """
    depends_id = call["data"].replace('depends_', '')
    one_depend = session.query(Vstup).filter(Vstup.id == depends_id).first()
    areas = session.query(Vstup).filter(Vstup.study_degree == one_depend.study_degree).filter(
        Vstup.depends_on == one_depend.depends_on).distinct(Vstup.area).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for area in areas:
        button = types.InlineKeyboardButton(text=area.area, callback_data=f'area_{area.id}-0')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'degree_{depends_id}')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose area')
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="degree_"))
async def get_depends_on(call: types.CallbackQuery):
    """
    Function change buttons after choose study degree, to choose user qualification(grounds for admission)
    degree_id: string contain id of Vstup object that contain chosen study degree
    one_degree: Vstup object that contain chosen study degree
    depends_data: list of Vstup objects that fit to chosen study degree with unique "depends_on"
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change keyboard of message
    """
    degree_id = call["data"].replace('degree_', '')
    one_degree = session.query(Vstup).filter(Vstup.id == degree_id).first()
    depends_data = session.query(Vstup).filter(Vstup.study_degree == one_degree.study_degree) \
        .distinct(Vstup.depends_on).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for depend in depends_data:
        button = types.InlineKeyboardButton(text=depend.depends_on, callback_data=f'depends_{depend.id}')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'start_')
    buttons.append(button)
    keyboard.add(*buttons)
    await call.message.edit_text('Choose qualification')
    await call.message.edit_reply_markup(keyboard)


@dp.message_handler(commands="start")
@dp.callback_query_handler(Text(startswith="start_"))
async def get_degree(message: types.Message):
    """
    Function creating buttons to choose study degree
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change/send keyboard of message
    degrees: list of Vstup objects with unique study degree
    """
    buttons = []
    degrees = session.query(Vstup).distinct(Vstup.study_degree).all()
    for degree in degrees:
        button = types.InlineKeyboardButton(text=degree.study_degree, callback_data=f'degree_{degree.id}')
        buttons.append(button)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text("Choose study degree")
        await message.message.edit_reply_markup(keyboard)
    else:
        await message.answer("Choose study degree", reply_markup=keyboard)


# Function to get or create object UserSubjects
async def set_user_subs(call):
    user_subs = session.query(UserSubjects).filter(UserSubjects.user_id == call["from"]["id"]).first()
    if not user_subs:
        user_subs = UserSubjects(user_id=call["from"]["id"])
        session.add(user_subs)
        session.commit()
    return user_subs


async def get_last(objects: list, first: int) -> int:
    if len(objects) <= first + 10:
        last = len(objects)
    else:
        last = first + 10
    return last


async def get_subjects_lists(data):
    optionally_subjects = []
    need_subjects = []
    for subject, coefficient in data.subjects.items():
        if subject.endswith('*'):
            optionally_subjects.append([subject, coefficient])
        else:
            need_subjects.append([subject, coefficient])
    return optionally_subjects, need_subjects


async def on_startup(_):
    print("Bot has been launched")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
