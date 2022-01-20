from sqlalchemy.orm import Session
from models import engine, UserSubjects

session = Session(bind=engine)


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


async def compare_grades(call, data, study_type):
    if study_type:
        user_sujbects = await set_user_subs(call)
        grades = await get_user_grades_dict(user_sujbects)
        optionally_subjects, need_subjects = await get_subjects_lists(data)
        result_grade = 0
        for n in need_subjects:
            current = grades.get(n[0])
            if current:
                result_grade += current * n[1]
            else:
                return False
        bigest_optional = 0
        for o in optionally_subjects:
            current = grades.get(o[0][:-1])
            if current:
                bigest_optional += current * o[1]
        if bigest_optional:
            result_grade += bigest_optional
            if study_type <= result_grade:
                return True
        return False


async def get_user_grades_dict(user_subjects):
    return {
        'Українська мова': user_subjects.sub1,
        'Українська мова та література': user_subjects.sub2,
        'Іноземна мова': user_subjects.sub3,
        'Історія України': user_subjects.sub4,
        'Математика': user_subjects.sub5,
        'Біологія': user_subjects.sub6,
        'Географія': user_subjects.sub7,
        'Фізика': user_subjects.sub8,
        'Хімія': user_subjects.sub9,
        'Середній бал документа про освіту': user_subjects.sub10
    }


async def message_of_pass(result_grade, previous_year_grade, call, type_of_edu):
    if result_grade >= previous_year_grade:
        await call.message.answer(f"You can pass {type_of_edu}")
    else:
        await call.message.answer(f"You can not pass {type_of_edu}")


async def set_information(speciality):
    information = f"Area: {speciality.area}\n"\
                  f"University: {speciality.university}\n"\
                  f"Department: {speciality.department}\n"\
                  f"Speciality: {speciality.speciality}\n"
    if speciality.avg_grade_for_contract:
        information += f"Average grade for contrat in lust year: {speciality.avg_grade_for_contract}\n"
    if speciality.avg_grade_for_budget:
        information += f"Average grade for budget in lust year: {speciality.avg_grade_for_budget}\n"
    if speciality.subjects:
        information += "Subjects and coefficients:\n"
        for subject, coefficient in speciality.subjects.items():
            information += f"{subject} : {coefficient}\n"
        information += "You only need one subject from those with an asterisk*"
    return information


async def set_text_for_grades(data, need_subjects_string, optionally_subjects_string):
    optionally_subjects, need_subjects = await get_subjects_lists(data)
    counter = 0
    for n in need_subjects:
        counter += 1
        need_subjects_string += f"/sub{counter} for {n[0]}\n"
    if optionally_subjects:
        optionally_subjects_string += f"/sub{counter + 1} for"
    for o in optionally_subjects:
        optionally_subjects_string += f" {o[0]},"
    optionally_subjects_string = optionally_subjects_string[:-1]
    return need_subjects_string, optionally_subjects_string


async def recalc_information(call, speciality):
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
    return result_grade
