from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import time
import re
from pymongo import MongoClient
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36}'}


def hh(main_link, search_str, number_of_pages):
    html = requests.get(
        main_link + '/search/vacancy?clusters=true&enable_snippets=true&text=' + search_str + '&showClusters=true',
        headers=headers).text
    parsed_site = BeautifulSoup(html, 'lxml')
    jobs = []
    for i in range(number_of_pages):
        jobs_block = parsed_site.find('div', {'class': 'vacancy-serp'})
        jobs_list = jobs_block.findChildren(recursive=False)
        for job in jobs_list:
            job_data = {}
            req = job.find('span', {'class': 'g-user-content'})
            if req is not None:
                main_info = req.findChild()
                job_name = main_info.getText()
                job_link = main_info['href']
                compensation = job.find('div', {'class': 'vacancy-serp-item__compensation'})
                if not compensation:
                    compensation_min = 0
                    compensation_max = 0
                else:
                    compensation = compensation.getText().replace(u'\xa0', u' ')
                    compensations = compensation.split('-')
                    compensation_min = compensations[0]
                    if len(compensations) > 1:
                        compensation_max = compensations[1]
                    else:
                        compensation_max = ''
                job_data['name'] = job_name
                job_data['compensation_min'] = compensation_min
                job_data['compensation_max'] = compensation_max
                job_data['link'] = job_link
                job_data['site'] = main_link
                jobs.append(job_data)
        next_btn_block = parsed_html.find('a', {'class': 'bloko-button HH-Pager-Controls-Next HH-Pager-Control'})
        next_btn_link = next_btn_block['href']
        html = requests.get(main_link + next_btn_link, headers=headers).text
        parsed_html = BeautifulSoup(html, 'lxml')

    jobs_db.insert_many(jobs)
    return jobs


def insert_data_to_db(search_str, number_of_pages):
    jobs_db.delete_many({})
    jobs_db.insert_many(hh('https://krasnodar.hh.ru', search_str, number_of_pages))


def find_salaries_greater_than(salary_greater_than):
    return jobs_db.find({'salary_greater_than': {'$gte': salary_greater_than}})


client = MongoClient('localhost', 27017)
db = client['jobs_db']
jobs_db = db.jobs_db
search_str = 'Python'
salary_greater_than = 80000
number_of_pages = 2

insert_data_to_db(search_str, number_of_pages)
records_db = find_salaries_greater_than(salary_greater_than)

for rec in records_db:
    pprint(rec)

count = jobs_db.count()
print('Записей в БД:', count)