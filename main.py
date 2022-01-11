import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import re


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


def get_area_universities(area):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }

    all_areas = get_areas_dict()
    url = all_areas.get(area)
    if url:
        r = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(r.text, "lxml")

        uni_dict = {}

        all_uni = soup.find("ul", class_="section-search-result-list").find_all("a")
        for uni in all_uni:
            uni_text = uni.text
            uni_url = f"{uni.get('href')}"
            uni_url_sized = f"{uni_url.split('/')[2]}/"
            if uni_text not in uni_dict:
                uni_dict[uni_text] = f"{url}{uni_url_sized}"
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
        department = dep.text.split("Факультет:")[1].split('Освітня')[0].strip()
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

    # for k, v in departments_dict.items():
    #     if v['zno']['old_contract']:
    #         print(v['zno']['old_contract'])

    g = {'Факультет будівництва та архітектури': {'191 Архітектура та містобудування':
                                                      {'zno': {'Українська мова та література ':
                                                                   ['100', '0.25'], 'Математика ':
                                                          ['100', '0.25'], 'Творче вступне випробування ':
                                                          ['100', '0.40'], 'Середній бал документа про освіту ':
                                                          ['0.10']}, 'old_contract': '132.00'}}}
    for k, v in departments_dict.items():
        for s, z in v.items():
            if z.get('old_contract'):
                print(f"{z.get('old_contract')} contract:)")
            if z.get('old_budget'):
                print(f"{z.get('old_budget')} budget:)")

    return departments_dict



if __name__ == '__main__':
    print(get_university_department('https://vstup.osvita.ua/r27/344/'))

