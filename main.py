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
    # print(areas_dict)
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
                uni_dict[uni_text] = {"university_name": uni_text, "university_url": f"{url}{uni_url_sized}"}
        return uni_dict

    else:
        return "Wrong area. Try again"


def get_university_department(university):
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        }

    all_departments = get_area_universities(university)

# if __name__ == '__main__':
#     print(get_area_universities('м. Київ'))