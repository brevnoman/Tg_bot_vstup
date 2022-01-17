import multiprocessing
import requests
from bs4 import BeautifulSoup
from models import engine, Base
from models import Vstup
from sqlalchemy.orm import Session

session = Session(bind=engine)

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}


def get_areas_dict():
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
        raise Exception("Wrong area. Try again")


def get_university_department(university_url):
    url = university_url
    r = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    deps_all = soup.select('div[class*="row no-gutters table-of-specs-item-row"]')
    departments_dict = {}
    counter = 0
    for dep in deps_all:
        if "Факультет:" in dep.text:
            department = dep.text.split("Факультет:")[1].split('Освітня')[0].strip()
        else:
            department = dep.text.split("Галузь:")[1].split('Спеціальність')[0].strip()
        speciality = dep.find("a").text
        grades_names = dep.select('div[class*="sub"]')
        stat_old = dep.find_all("div", class_="stat_old")
        counter += 1
        grades_dict = {}
        for grade in range(0, len(grades_names), 2):
            grades_dict[grades_names[grade].text.split("(")[0].strip()] = grades_names[grade].text.replace(" \n",
                                                                                                           "").replace(
                ")", "").replace(", ", "").replace("балmin=", "k=").strip().split("k=")[1:3]
        if department not in departments_dict.keys():
            departments_dict[department] = {}
        if speciality not in departments_dict[department]:
            departments_dict[department].setdefault(f"speciality{counter}", {})
            departments_dict[department][f"speciality{counter}"][speciality] = {"zno": grades_dict}
        if len(stat_old) == 2:
            departments_dict[department][f"speciality{counter}"][speciality]["old_budget"] = float(
                stat_old[0].text.split(": ")[1])
            departments_dict[department][f"speciality{counter}"][speciality]["old_contract"] = float(
                stat_old[1].text.split(": ")[1])
        elif len(stat_old) == 1:
            departments_dict[department][f"speciality{counter}"][speciality]["old_contract"] = float(
                stat_old[0].text.split(": ")[1].strip())
        study_degree = dep.text.split("Спеціальність")[1].split(" (")[0].strip()
        depends_on = dep.text.split("(")[1].split(")")[0].strip()
        departments_dict[department][f"speciality{counter}"][speciality]["depends_on"] = depends_on.strip()
        departments_dict[department][f"speciality{counter}"][speciality]["study_degree"] = study_degree.strip()

    return departments_dict


def process_purs(university_count, area, area_url, university, university_url):
    print(university_count)
    departments = get_university_department(university_url)
    for department, value in departments.items():
        for key, value_for_each_faculty in value.items():
            speciality = list(value_for_each_faculty.keys())[0]
            faculty = Vstup(area=area,
                            area_url=area_url,
                            university=university,
                            university_url=university_url,
                            department=department,
                            speciality=speciality
                            )
            counter = 0
            subjects = {}
            for subject, coefficient in value_for_each_faculty[speciality]['zno'].items():
                counter += 1
                if len(coefficient) == 1:
                    subjects[subject] = float(coefficient[0])
                else:
                    subjects[subject] = float(coefficient[1])
            if value_for_each_faculty[speciality].get("old_budget"):
                faculty.avg_grade_for_budget = float(value_for_each_faculty[speciality].get("old_budget"))
            if value_for_each_faculty[speciality].get("old_contract"):
                faculty.avg_grade_for_contract = float(value_for_each_faculty[speciality].get("old_contract"))
            faculty.depends_on = value_for_each_faculty[speciality].get("depends_on")
            faculty.study_degree = value_for_each_faculty[speciality].get("study_degree")
            faculty.subjects = subjects
            session.add(faculty)


def get_all_to_db_processing():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    areas = get_areas_dict()
    university_count = 0
    for area, area_url in areas.items():
        universities = get_area_universities(area_url)
        for university, university_url in universities.items():
            university_count += 1
            process = multiprocessing.Process(
                target=process_purs(university_count=university_count, area=area, area_url=area_url,
                                    university=university, university_url=university_url,
                                    )
            )
            process.start()
    session.commit()
#
# if __name__ == '__main__':
#     get_all_to_db_processing()