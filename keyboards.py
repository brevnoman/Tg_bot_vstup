from aiogram import types

from utils import get_last, compare_grades

next_emoji = u"\u27A1"
previous_emoji = u'\u2b05'


async def start_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text="Find by speciality", callback_data="choose_degree_"),
               types.InlineKeyboardButton(text="Find with grades", callback_data="find_area_")]
    keyboard.add(*buttons)
    return keyboard


async def grades_area_keyboard(session, vstup):
    areas = session.query(vstup).filter(vstup.study_degree == "Бакалавр", vstup.depends_on == "на основі Повна загальна середня освіта").distinct(vstup.area).all()
    buttons = []
    keyboard = types.InlineKeyboardMarkup()
    for area in areas:
        button = types.InlineKeyboardButton(text=area.area, callback_data=f"find_uni_{area.id}_0")
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'start_')
    buttons.append(button)
    keyboard.add(*buttons)
    return keyboard

async def grades_universities_keyboard(area_id, first, universities):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    last = await get_last(first=first, objects=universities)
    for university in range(first, last):
        button = types.InlineKeyboardButton(text=universities[university].university, callback_data=f"get_grades_{universities[university].id}")
        buttons.append(button)
    if first:
        buttons.append(types.InlineKeyboardButton(text=f"Previous " + previous_emoji,
                                                  callback_data=f'find_uni_{area_id}_{first - 10}'))
    if last != len(universities):
        buttons.append(types.InlineKeyboardButton(text="Next " + next_emoji,
                                                  callback_data=f'find_uni_{area_id}_{last}'))
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'find_area_{universities[0].id}')
    buttons.append(button)
    keyboard.add(*buttons)
    return keyboard


async def get_grades_keyboard(uni_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(text="Find", callback_data=f"find_it_{uni_id}_0"),
        types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'find_uni_{uni_id}_0')
    ]
    keyboard.add(*buttons)
    return buttons

async def find_it_keyboard(call, specialities):
    data = call["data"].replace("find_it_", "").split("_")
    uni_id = data[0]
    first = int(data[1])
    buttons = []
    all_buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for speciality in specialities:
        if await compare_grades(call=call, data=speciality, study_type=speciality.avg_grade_for_budget):
            all_buttons.append(
                types.InlineKeyboardButton(text=f"Budget {speciality.speciality}", callback_data=f"more_grade_{speciality.id}")
            )
        if await compare_grades(call=call, data=speciality, study_type=speciality.avg_grade_for_contract):
            all_buttons.append(
                types.InlineKeyboardButton(text=f"Contract {speciality.speciality}", callback_data=f"more_grade_{speciality.id}")
            )
    last = await get_last(objects=all_buttons, first=first)
    for index in range(first, last):
        buttons.append(all_buttons[index])
    if first:
        buttons.append(types.InlineKeyboardButton(text=f"Previous " + previous_emoji,
                                                  callback_data=f'find_it_{uni_id}_{first - 10}'))
    if last != len(all_buttons):
        buttons.append(types.InlineKeyboardButton(text="Next " + next_emoji,
                                                  callback_data=f'find_it_{uni_id}_{last}'))
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'find_uni_{uni_id}_0')
    buttons.append(button)
    keyboard.add(*buttons)
    return keyboard, buttons

async def more_information_keyboard(spec_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(text="Return" + u"\u274C",
                                                  callback_data=f'find_it_{spec_id}_0'))
    return keyboard

async def get_degree_keyboard(degrees):
    buttons = []
    for degree in degrees:
        button = types.InlineKeyboardButton(text=degree.study_degree, callback_data=f'degree_{degree.id}')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return" + u"\u274C",
                                                  callback_data=f'start_')
    buttons.append(button)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


async def get_depends_on_keyboard(depends_data):
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for depend in depends_data:
        button = types.InlineKeyboardButton(text=depend.depends_on, callback_data=f'depends_{depend.id}')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'choose_degree_')
    buttons.append(button)
    keyboard.add(*buttons)
    return keyboard

async def get_areas_keyboard(areas, depends_id):
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for area in areas:
        button = types.InlineKeyboardButton(text=area.area, callback_data=f'area_{area.id}-0')
        buttons.append(button)
    button = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'degree_{depends_id}')
    buttons.append(button)
    keyboard.add(*buttons)
    return keyboard


async def get_universities_keyboard(call, universities):
    area_data = call["data"].replace('area_', '').split("-")
    area_id = area_data[0]
    first = int(area_data[1])
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
    return keyboard

async def get_department_keyboard(call, departments):
    uni_data = call["data"].replace('uni_', '').split("-")
    university_id = uni_data[0]
    first = int(uni_data[1])
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
    return keyboard


async def get_speciality_keyboard(call, specialities):
    dep_data = call["data"].replace('dep_', '').split("-")
    department_id = dep_data[0]
    first = int(dep_data[1])
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
    return keyboard

async def get_data_subjects_keyboard(data):
    buttons = []
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_return = types.InlineKeyboardButton(text="Return" + u"\u274C", callback_data=f'dep_{data.id}-0')
    buttons.append(button_return)
    button_calculate = types.InlineKeyboardButton(text="Calculate", callback_data=f'recalc_{data.id}')
    buttons.append(button_calculate)
    keyboard.add(*buttons)
    return keyboard