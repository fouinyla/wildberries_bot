import httpx
from bs4 import BeautifulSoup
import json
import xlsxwriter
from . import time
import os
import datetime
import string
from typing import Tuple, List, Dict
from const.const import *

COOKIES_PART = '_ym_uid=1651240592234847018; _ym_d=1651240592; ' \
    '_ga=GA1.1.2054104203.1651240592; _ym_isad=2; ' \
    'supportOnlineTalkID=r85EpoyBIxTRA3agMH9GXs5yZQOApJun; ' \
    '_ym_hostIndex=0-3%2C1-0; _ym_visorc=w; ' \
    'userlogin=a%3A2%3A%7Bs%3A3%3A%22lgn%22%3Bs%3A29%3A%22ip.' \
    'evgeniy.bogdanov%40gmail.com%22%3Bs%3A3%3A%22pwd%22%3Bs%' \
    '3A32%3A%2299fa197de27558f79782ea8373471beb%22%3B%7D; ' \
    '_ga_8S8Y1X62NG=GS1.1.1651240592.1.1.1651240652.0'

# создание директории для записи данных
os.makedirs('results', exist_ok=True)


def get_trends_data(path: str, view: str) -> List[Dict]:
    """
        path: 'Детям/Детское питание/Детская смесь' (example)
        view: 'category' or 'itemsInCategory'
    """
    with httpx.Client() as client:
        main_page_response = client.get(MPSTATS_MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookie = main_page_response.headers['set-cookie']
        trends_response = client.get(MPSTATS_TRENDS_URL,
                                     headers={'cookie': cookie + COOKIES_PART},
                                     params={'view': view,
                                             'path': path},
                                     follow_redirects=True)
        trends_response.raise_for_status()
        return trends_response.json()


def get_seo(queries: str) -> Tuple[str, bool]:
    flag_all_queries_are_empty = True  # флаг, если все запросы пустые
    queries = queries.split('\n')
    today_date = time.get_moscow_datetime().date()
    with httpx.Client() as client:
        # получение кук для отправки запроса для получения SKU
        main_page_response = client.get(MPSTATS_MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookies = main_page_response.headers['set-cookie']
        headers = {'cookie': cookies + COOKIES_PART}
        # создание excel-файла для записи данных
        what_to_delete = queries[0].maketrans('', '', string.punctuation)
        query_for_tablename = queries[0].translate(what_to_delete)
        if not query_for_tablename:
            query_for_tablename = 'символьный_запрос'
        path_to_excel = f'results/SEO_{query_for_tablename[0:30]}_{today_date}.xlsx'

        try:
            workbook = xlsxwriter.Workbook(path_to_excel)
            for num, query in enumerate(queries, start=1):
                # запрос на получение html с SKU
                sku_response = client.get(MPSTATS_SKU_URL,
                                          headers=headers,
                                          params={'query': query},
                                          follow_redirects=True)
                sku_response.raise_for_status()
                # парсинг html ответа для получения SKU
                html = sku_response.text
                soup = BeautifulSoup(html, 'lxml')
                tpls = soup.find('wb-search-result')
                if not tpls:
                    continue
                flag_all_queries_are_empty = False
                attributes = [sku for _, sku in json.loads(tpls['tpls'])]
                # получение запросов по атрибутам
                data = {'query': ','.join(map(str, attributes)),
                        'type': 'sku',
                        'similar': 'false',
                        'stopWords': [],
                        'searchFullWord': False,
                        'd1': today_date - datetime.timedelta(days=30),
                        'd2': today_date}
                response = client.post(MPSTATS_SEO_URL,
                                       headers=headers,
                                       data=data)
                response.raise_for_status()
                result = response.json()['result']
                # создание страницы в excel-файле с названиями колонок
                what_to_delete = query.maketrans('', '', string.punctuation)
                query_for_worksheet = query.translate(what_to_delete)
                query_for_worksheet = query_for_worksheet[0:28] + str(num)
                if not query_for_worksheet:
                    query_for_worksheet = 'Символьный запрос'
                worksheet = workbook.add_worksheet(name=query_for_worksheet)
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
    return path_to_excel, flag_all_queries_are_empty
