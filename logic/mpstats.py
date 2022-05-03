from attr import attr, attrib
import httpx
from bs4 import BeautifulSoup
import json
from typing import List
import xlsxwriter
from . import time
import os
import datetime


MAIN_PAGE_URL = 'https://mpstats.io/'
BASE_SKU_GETTING_URL = 'https://mpstats.io/wb/bysearch?'
BASE_SKU_GETTING_SEO = 'https://mpstats.io/api/seo/keywords/expanding'

COOKIES_PART = '_ym_uid=1651240592234847018; _ym_d=1651240592; ' \
              '_ga=GA1.1.2054104203.1651240592; _ym_isad=2; ' \
              'supportOnlineTalkID=r85EpoyBIxTRA3agMH9GXs5yZQOApJun; ' \
              '_ym_hostIndex=0-3%2C1-0; _ym_visorc=w; ' \
              'userlogin=a%3A2%3A%7Bs%3A3%3A%22lgn%22%3Bs%3A29%3A%22ip.' \
              'evgeniy.bogdanov%40gmail.com%22%3Bs%3A3%3A%22pwd%22%3Bs%' \
              '3A32%3A%2299fa197de27558f79782ea8373471beb%22%3B%7D; ' \
              '_ga_8S8Y1X62NG=GS1.1.1651240592.1.1.1651240652.0'


def get_SEO(queries: str, tg_id: str) -> str:
    flag_all_empty_queries = 1  # флаг, если все запросы пользователя пустые
    queries = queries.split('\n')
    today_date = time.get_moscow_datetime().date()
    with httpx.Client(timeout=120) as client: #timeout?
        # получение кук для отправки запроса для получения SKU
        main_page_response = client.get(MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookies = main_page_response.headers['set-cookie']
        headers={'cookie': cookies + COOKIES_PART}
        try:
            # создание excel-файла для записи данных
            path_to_excel = f"results/SEO_{tg_id}_{today_date}.xlsx"
            workbook = xlsxwriter.Workbook(path_to_excel)
            for query in queries:
                # запрос на получение html с SKU
                sku_response = client.get(BASE_SKU_GETTING_URL,
                                        headers=headers,
                                        params={'query': query})
                sku_response.raise_for_status()
                # парсинг html ответа для получения SKU
                html = sku_response.text
                soup = BeautifulSoup(html, 'lxml')
                tpls = soup.find('wb-search-result')
                if tpls:
                    data = json.loads(tpls['tpls'])
                    flag_all_empty_queries = 0
                else:
                    continue
                attributes = [sku for _, sku in data]
                # получение запросов по атрибутам
                data = {"query": ','.join(map(str, attributes)),
                        "type": "sku",
                        "similar": "false",
                        "stopWords": [],
                        "searchFullWord": False,
                        "d1": today_date - datetime.timedelta(days=30),
                        "d2": today_date}
                response = client.post(BASE_SKU_GETTING_SEO, headers=headers, data=data)
                result = response.json()['result']
                # создание страницы в excel-файле с названиями колонок
                worksheet = workbook.add_worksheet(name = query)
                worksheet.write(0, 0, 'Слово')
                worksheet.write(0, 1, 'Словоформы')
                worksheet.write(0, 2, 'Количество вхождений')
                worksheet.write(0, 3, 'Суммарная частотность')
                # запись данных в excel-файл
                for row, word in enumerate(result, start=1):
                    if word['count'] > 1:
                        worksheet.write(row, 0, word['word'])
                        worksheet.write(row, 1, ', '.join(word['words']))
                        worksheet.write(row, 2, str(word['count']))
                        worksheet.write(row, 3, str(word['keys_count_sum']))
        finally:
            workbook.close()
    return (path_to_excel, flag_all_empty_queries)

# get_SEO('свитер\nсвитер женский\nсвитер оверсайз')