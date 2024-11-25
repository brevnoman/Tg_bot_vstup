from config import token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text

from keyboards import start_keyboard, grades_area_keyboard, grades_universities_keyboard, get_grades_keyboard, \
    find_it_keyboard, more_information_keyboard, get_degree_keyboard, get_depends_on_keyboard, get_areas_keyboard, \
    get_universities_keyboard, get_department_keyboard, get_speciality_keyboard, get_data_subjects_keyboard
from models import engine, Vstup
from sqlalchemy.orm import Session

from utils import set_information, set_user_subs, set_text_for_grades, recalc_information

bot = Bot(token=token)
dp = Dispatcher(bot)
session = Session(bind=engine)


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
    result_grade = await recalc_information(call=call, speciality=speciality)
    if not speciality.avg_grade_for_budget and not speciality.avg_grade_for_contract:
        await call.message.answer("We have no data about previous years contract or budget average grade(")
    await call.message.answer(text=f"Your average grade is {result_grade}")


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
            if 1 > int(subject_number) or int(subject_number) > 10 or 100 > int(subject_grade) or int(
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
    need_subjects_string = ""
    optionally_subjects_string = ""
    need_subjects_string, optionally_subjects_string = await set_text_for_grades(data=data,
                                                                                 need_subjects_string=need_subjects_string,
                                                                                 optionally_subjects_string=optionally_subjects_string)
    await call.message.edit_text(f'Enter next subjects as in example\n'
                                 f'Example "/sub1 190"\n'
                                 f'{need_subjects_string}'
                                 f'{optionally_subjects_string}\n'
                                 f'When you will enter all grades press Calculate button'
                                 )
    await call.message.edit_reply_markup(await get_data_subjects_keyboard(data=data))


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
    user_subs = await set_user_subs(call)
    user_subs.set_default()
    session.commit()
    one_dep = session.query(Vstup).filter(Vstup.id == department_id).first()
    specialities = session.query(Vstup).filter(Vstup.depends_on == one_dep.depends_on).filter(
        Vstup.study_degree == one_dep.study_degree).filter(Vstup.university_url == one_dep.university_url).filter(
        Vstup.department == one_dep.department).distinct(Vstup.speciality).all()
    await call.message.edit_text('Choose speciality')
    await call.message.edit_reply_markup(await get_speciality_keyboard(call=call, specialities=specialities))


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
    departments = session.query(
        Vstup).filter(
        Vstup.university_url == one_uni.university_url).filter(
        Vstup.study_degree == one_uni.study_degree).filter(
        Vstup.depends_on == one_uni.depends_on).distinct(
        Vstup.department).all()
    await call.message.edit_text('Choose department')
    await call.message.edit_reply_markup(await get_department_keyboard(call=call, departments=departments))


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
    one_area = session.query(Vstup).filter(Vstup.id == area_id).first()
    universities = session.query(
        Vstup).filter(
        Vstup.area_url == one_area.area_url).filter(
        Vstup.study_degree == one_area.study_degree).filter(
        Vstup.depends_on == one_area.depends_on).distinct(
        Vstup.university_url).all()
    await call.message.edit_text('Choose university')
    await call.message.edit_reply_markup(await get_universities_keyboard(call=call, universities=universities))


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
    await call.message.edit_text('Choose area')
    await call.message.edit_reply_markup(await get_areas_keyboard(areas=areas, depends_id=depends_id))


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
    await call.message.edit_text('Choose qualification')
    await call.message.edit_reply_markup(await get_depends_on_keyboard(depends_data=depends_data))



@dp.callback_query_handler(Text(startswith="choose_degree_"))
async def get_degree(message: types.CallbackQuery):
    """
    Function creating buttons to choose study degree
    buttons: list contains InlineKeyboardButton objects
    keyboard: InlineKeyboardMarkup object used to change/send keyboard of message
    degrees: list of Vstup objects with unique study degree
    """
    degrees = session.query(Vstup).distinct(Vstup.study_degree).all()
    await message.message.edit_text("Choose study degree")
    await message.message.edit_reply_markup(await get_degree_keyboard(degrees=degrees))


@dp.callback_query_handler(Text(startswith="more_grade_"))
async def more_information(call: types.CallbackQuery):
    spec_id = int(call['data'].replace("more_grade_", ""))
    speciality: Vstup = session.query(Vstup).filter(Vstup.id == spec_id).first()
    information = await set_information(speciality=speciality)
    await call.message.edit_text(
        text=information
    )
    await call.message.edit_reply_markup(await more_information_keyboard(spec_id=spec_id))


@dp.callback_query_handler(Text(startswith="find_it_"))
async def find_it(call: types.CallbackQuery):
    data = call["data"].replace("find_it_", "").split("_")
    uni_id = data[0]
    university = session.query(Vstup).filter(
        Vstup.id == uni_id,
    ).first()
    specialities = session.query(Vstup).filter(
        Vstup.university == university.university,
        Vstup.depends_on == university.depends_on,
        Vstup.study_degree == university.study_degree,
        Vstup.avg_grade_for_contract.is_not(None)
    ).distinct(
        Vstup.speciality,
        Vstup.depends_on
    ).all()
    keyboard, buttons = await find_it_keyboard(call=call, specialities=specialities)
    if len(buttons) > 1:
        await call.message.edit_text(f"Specialities in {specialities[0].university} that you can pass")
    else:
        await call.message.edit_text("retard")
    await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(Text(startswith="get_grades_"))
async def get_grades(call: types.CallbackQuery):
    uni_id = call["data"].replace("get_grades_", "")
    await call.message.edit_text(
        'Enter next subjects as in example\n'
        'Example "/sub1 190"\n'
        '/sub1 for Українська мова\n'
        '/sub2 for Українська мова та література\n'
        '/sub3 for Іноземна мова\n'
        '/sub4 for Історія України\n'
        '/sub5 for Математика\n'
        '/sub6 for Біологія\n'
        '/sub7 for Географія\n'
        '/sub8 for Фізика\n'
        '/sub9 for Хімія\n'
        '/sub10 for Середній бал документа про освіту\n'
        'When you will enter all your grades press "Find" button'
    )
    await call.message.edit_reply_markup(await get_grades_keyboard(uni_id=uni_id))


@dp.callback_query_handler(Text(startswith="find_uni_"))
async def grades_universities(call: types.CallbackQuery):
    data = call["data"].replace("find_uni_", "").split("_")
    area_id = data[0]
    first = int(data[1])
    area = session.query(Vstup).filter(Vstup.id == area_id).first()
    universities = session.query(Vstup).filter(
        Vstup.depends_on == area.depends_on,
        Vstup.study_degree == area.study_degree,
        Vstup.area == area.area,
        Vstup.avg_grade_for_contract.is_not(None)
    ).distinct(Vstup.university).all()
    await call.message.edit_text("Choose university")
    await call.message.edit_reply_markup(await grades_universities_keyboard(area_id=area_id, first=first, universities=universities))


@dp.callback_query_handler(Text(startswith="find_area_"))
async def grades_area(call: types.CallbackQuery):
    await call.message.edit_text("Chose university")
    await call.message.edit_reply_markup(await grades_area_keyboard(session=session, vstup=Vstup))


@dp.message_handler(commands="start")
async def chose_way(message: types.Message):
    await message.answer("Choose", reply_markup=await start_keyboard())


@dp.callback_query_handler(Text(startswith="start_"))
async def change_chose_way(call: types.CallbackQuery):
    await call.message.edit_text("Choose")
    await call.message.edit_reply_markup(await start_keyboard())


async def on_startup(_):
    print("Bot has been launched")


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
