import datetime
from pprint import pprint

import aiohttp
import asyncio
from bs4 import BeautifulSoup

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                  " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
}

async def get_areas_dict(session) -> dict:
    """
    Method for parsing all areas and area urls from vstup.osvita.ua
    """
    url = "https://vstup.osvita.ua"
    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), "lxml")

        areas_dict = {}

        select_list_areas = soup.find("select", class_="region-select").find_all("option")
        for option in select_list_areas:
            if option not in areas_dict:
                option_text = option.text
                option_value = option.get("value")
                if option_value:
                    areas_dict[option_text] = f"{url}{option_value}"

        return areas_dict

async def get_area_universities(session, area_url: str) -> dict:
    """
    Method that get all universities and university urls for one area
    """
    if area_url:
        async with session.get(area_url, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), "lxml")

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


async def parse_one_speciality(session, speciality_url):
    url = speciality_url
    async with session.get(url, headers=headers) as response:
        speciality = BeautifulSoup(await response.text(), "lxml")
        link_2020 = speciality.find("table", class_="stats-vnz-table")
        if link_2020:
            url = "https://vstup.osvita.ua" + link_2020.find("a").get("href")
            async with session.get(url, headers=headers) as response:
                speciality_2020 = BeautifulSoup(await response.text(), "lxml")
                avg_grades = speciality_2020.find("table", class_="stats-vnz-table").select('tr')
                min_budget = None
                avg_contract = None
                for row in avg_grades:
                    info_list = row.select("td")
                    if info_list[0].text == "Мінімальний рейтинговий бал серед зарахованих на бюджет":
                        min_budget = info_list[1].text
                    if info_list[0].text == 'Середній рейтинговий бал зарахованих на контракт':
                        avg_contract = info_list[1].text
                return min_budget, avg_contract
        return None, None



async def get_university_department(session, university, university_url: str) -> dict:
    """
    Method that parse every department for one university
    """
    url = university_url
    async with session.get(url, headers=headers) as response:
        soup = BeautifulSoup(await response.text(), "lxml")
        deps_all = soup.find("div", class_="panel den")
        if deps_all:
            deps_all = deps_all.select('div[class*="row no-gutters table-of-specs-item-row qual1 base40"]')
        if deps_all:
            departments_dict = {}
            counter = 0
            for dep in deps_all:
                try:
                    department = dep.text.split("Факультет:")[1]
                    department = department.split('Освітня')[0].strip()
                except IndexError:
                    department = "-"
                knowledge_area = dep.text.split("Галузь:")[1].split('Спеціальність')[0].strip()
                speciality = dep.find("a").text
                program = dep.text.split("Освітня програма:")[1].split("\n")[0].strip()
                speciality_url = "https://vstup.osvita.ua" + dep.find("a", class_="green-button").get("href")
                grades_names = dep.select('div[class*="sub"]')
                counter += 1
                grades_dict = {}
                for grade in range(0, len(grades_names), 2):
                    name = grades_names[grade].text.split("(")[0].strip()
                    coefficient = grades_names[grade].text.replace(" \n", "").replace(")", "").replace(", ",
                                                                                                       "").replace(
                        "балmin=", "k=").strip().split("k=")[1:3]
                    if len(coefficient) > 1:
                        grades_dict[name] = coefficient[1]
                    else:
                        grades_dict[name] = coefficient[0]
                if department not in departments_dict.keys():
                    departments_dict[department] = {}
                if speciality not in departments_dict[department]:
                    departments_dict[department].setdefault(f"speciality{counter}", {})
                    departments_dict[department][f"speciality{counter}"][speciality] = {"zno": grades_dict}
                min_budget, avg_contract = await parse_one_speciality(session, speciality_url)
                departments_dict[department][f"speciality{counter}"][speciality]["old_budget"] = min_budget
                departments_dict[department][f"speciality{counter}"][speciality]["old_contract"] = avg_contract
                departments_dict[department][f"speciality{counter}"][speciality]["knowledge_area"] = knowledge_area
                departments_dict[department][f"speciality{counter}"][speciality]["program"] = program
            return (university, departments_dict)


async def process_area(session, area, area_url):
    universities = await get_area_universities(session, area_url)
    tasks = []
    uni_dict = {}
    for university, university_url in universities.items():
        tasks.append(asyncio.ensure_future(get_university_department(session, university, university_url)
        ))
    for university_dict in await asyncio.gather(*tasks):
        if university_dict:
            uni_dict[university_dict[0]] = university_dict[1]
    return {area: uni_dict}

async def main():
    start = datetime.datetime.now()
    areas_count = 0
    async with aiohttp.ClientSession() as session:
        areas = await get_areas_dict(session)
        tasks = []
        for area, area_url in areas.items():
            if areas_count > 1:
                break
            areas_count += 1
            print(f"Processing area {area}")
            tasks.append(asyncio.ensure_future(
                process_area(session, area, area_url)
            ))
        done = await asyncio.gather(*tasks)
        # areas = await asyncio.wait(tasks)
        print(datetime.datetime.now() - start)
        return done


pprint(asyncio.run(main()))