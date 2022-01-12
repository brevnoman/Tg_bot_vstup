import requests
from bs4 import BeautifulSoup
from models import engine, Session
from datetime import datetime
import time
import json
import re

from models import Vstup


def get_areas_list():
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    url = "https://vstup.osvita.ua"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    areas_list = []

    select_list_areas = soup.find("select", class_="region-select").find_all("option")
    for option in select_list_areas:
        if option not in areas_list:
            option_text = option.text
            option_value = option.get("value")
            if option_value:
                areas_list.append(f"{option_text}")

    return areas_list

def get_areas_dict():
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    url = "https://vstup.osvita.ua"
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    areas_dict = {}

    select_list_areas = soup.find("select", class_="region-select").find_all("option")
    for option in select_list_areas:
        if option not in areas_dict:
            option_text = option.text
            option_value = option.get("value")
            if option_value:
                areas_dict[option_text] = f"{url}{option_value}"
    return areas_dict


def get_area_universities(area_url):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    # all_areas = get_areas_dict()
    # url = all_areas.get(area)
    if area_url:
        r = requests.get(url=area_url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        uni_dict = {}

        all_uni = soup.find("ul", class_="section-search-result-list").find_all("a")
        for uni in all_uni:
            uni_text = uni.text
            uni_url = f"{uni.get('href')}"
            uni_url_sized = f"{uni_url.split('/')[2]}/"
            if uni_text not in uni_dict:
                uni_dict[uni_text] = f"{area_url}{uni_url_sized}"
        return uni_dict

    else:
        return "Wrong area. Try again"


def get_university_department(university_url):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        }
    url = university_url
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    deps_all = soup.select('div[class*="row no-gutters table-of-specs-item-row"]')
    # print(deps_all)
    departments_dict = {}
    for dep in deps_all:
        if "Факультет:" in dep.text:
            department = dep.text.split("Факультет:")[1].split('Освітня')[0].strip()
        else:
            department = dep.text.split("Галузь:")[1].split('Спеціальність')[0].strip()
        speciality = dep.find("a").text
        grades_names = dep.select('div[class*="sub"]')
        stat_old = dep.find_all("div", class_="stat_old")

        grades_dict = {}
        for grade in range(0, len(grades_names), 2):
            grades_dict[grades_names[grade].text.split("(")[0]] = grades_names[grade].text.replace(" \n","").replace(")", "").replace(", ", "").replace("балmin=", "k=").split("k=")[1:3]
        if department not in departments_dict.keys():
            departments_dict[department] = {}
        if speciality not in departments_dict[department]:
            departments_dict[department].setdefault(speciality, {"zno": grades_dict})
        if len(stat_old) == 2:
            departments_dict[department][speciality]["old_budget"] = stat_old[0].text.split(": ")[1]
            departments_dict[department][speciality]["old_contract"] = stat_old[1].text.split(": ")[1]
        elif len(stat_old) == 1:
            departments_dict[department][speciality]["old_contract"] = stat_old[0].text.split(": ")[1]

    return departments_dict


def get_all_to_db():
    session = Session(bind=engine)
    areas = get_areas_dict()
    university_count = 0
    for area, area_url in areas.items():
        universities = get_area_universities(area_url)
        for university, university_url in universities.items():
            university_count += 1
            departments = get_university_department(university_url)
            print(university_count)
            for department, value in departments.items():
                for key, value_for_each_faculty in value.items():
                    faculty = Vstup(area=area,
                                    area_url=area_url,
                                    university=university,
                                    university_url=university_url,
                                    department=department,
                                    speciality=key
                                    )
                    counter = 0
                    third_subjects = []
                    for subject, coefficient in value_for_each_faculty['zno'].items():
                        counter += 1
                        if "*" not in subject and counter==1:
                            faculty.first_main_subject = subject
                            if len(coefficient)==1:
                                faculty.first_main_subject_grade_coefficient = float(coefficient[0])
                            else:
                                faculty.first_main_subject_grade_coefficient = float(coefficient[1])
                        elif "*" not in subject and counter==2:
                            faculty.second_main_subject = subject
                            if len(coefficient)==1:
                                faculty.second_main_subject_grade_coefficient = float(coefficient[0])
                            else:
                                faculty.second_main_subject_grade_coefficient = float(coefficient[1])

                        elif "*" in subject and len(subject)<20:
                            third_subjects.append(subject)
                            if len(coefficient)==1:
                                faculty.third_subject_grade_coefficient = float(coefficient[0])
                            else:
                                faculty.third_subject_grade_coefficient = float(coefficient[1])
                        elif subject == 'Середній бал документа про освіту ':
                            if len(coefficient)==1:
                                faculty.school_certificate_coefficient = float(coefficient[0])
                            else:
                                faculty.school_certificate_coefficient = float(coefficient[1])
                        elif subject == 'Бал за успішне закінчення підготовчих курсів закладу освіти ':
                            if len(coefficient)==1:
                                faculty.course_certificate_grade_coefficient = float(coefficient[0])
                            else:
                                faculty.course_certificate_grade_coefficient = float(coefficient[1])
                    if value_for_each_faculty.get("old_budget"):
                        faculty.avg_grade_for_budget = float(value_for_each_faculty.get("old_budget"))
                    if value_for_each_faculty.get("old_contract"):
                        faculty.avg_grade_for_contract = float(value_for_each_faculty.get("old_contract"))
                    if len(third_subjects)>0:
                        faculty.third_subject = third_subjects
                    session.add(faculty)
    session.commit()



if __name__ == '__main__':
    # print(get_university_department('https://vstup.osvita.ua/r9/91/'))
    get_all_to_db()