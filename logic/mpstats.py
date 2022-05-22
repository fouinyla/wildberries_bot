import httpx
from bs4 import BeautifulSoup
import json
import xlsxwriter
from . import time
import os
import datetime
import string
from typing import Tuple
import string


MAIN_PAGE_URL = 'https://mpstats.io/'
BASE_SKU_GETTING_URL = 'https://mpstats.io/wb/bysearch?'
BASE_SKU_GETTING_SEO = 'https://mpstats.io/api/seo/keywords/expanding'
BASE_PRICE_SEGMENTATION_URL = 'https://mpstats.io/api/wb/get/category/price_segmentation?'

COOKIES_PART = '_ym_uid=1651240592234847018; _ym_d=1651240592; ' \
    '_ga=GA1.1.2054104203.1651240592; _ym_isad=2; ' \
    'supportOnlineTalkID=r85EpoyBIxTRA3agMH9GXs5yZQOApJun; ' \
    '_ym_hostIndex=0-3%2C1-0; _ym_visorc=w; ' \
    'userlogin=a%3A2%3A%7Bs%3A3%3A%22lgn%22%3Bs%3A29%3A%22ip.' \
    'evgeniy.bogdanov%40gmail.com%22%3Bs%3A3%3A%22pwd%22%3Bs%' \
    '3A32%3A%2299fa197de27558f79782ea8373471beb%22%3B%7D; ' \
    '_ga_8S8Y1X62NG=GS1.1.1651240592.1.1.1651240652.0'

# создание директории для записи данных
path_to_results = os.path.join(os.getcwd(), 'results')
if not os.path.exists(path_to_results):
    os.makedirs(path_to_results)


def get_SEO(queries: str) -> Tuple[str, bool]:
    flag_all_queries_are_empty = True  # флаг, если все запросы пользователя пустые
    queries = queries.split('\n')
    today_date = time.get_moscow_datetime().date()
    with httpx.Client(timeout=120) as client:
        # получение кук для отправки запроса для получения SKU
        main_page_response = client.get(MAIN_PAGE_URL)
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
                sku_response = client.get(BASE_SKU_GETTING_URL,
                                          headers=headers,
                                          params={'query': query}, follow_redirects=True)
                sku_response.raise_for_status()
                # парсинг html ответа для получения SKU
                html = sku_response.text
                soup = BeautifulSoup(html, 'lxml')
                tpls = soup.find('wb-search-result')
                if not tpls:
                    continue
                data = json.loads(tpls['tpls'])
                flag_all_queries_are_empty = False
                attributes = [sku for _, sku in data]
                # получение запросов по атрибутам
                data = {'query': ','.join(map(str, attributes)),
                        'type': 'sku',
                        'similar': 'false',
                        'stopWords': [],
                        'searchFullWord': False,
                        'd1': today_date - datetime.timedelta(days=30),
                        'd2': today_date}
                response = client.post(BASE_SKU_GETTING_SEO,
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
                worksheet.set_column(0, 3, 15)
                worksheet.set_column(1, 1, 90)
                header_format = workbook.add_format({'bold': True, 'text_wrap': True, \
                                                'bg_color': '#D9D9D9', 'valign': 'vcenter'})
                worksheet.write(0, 0, 'Слово', header_format)
                worksheet.write(0, 1, 'Словоформы', header_format)
                worksheet.write(0, 2, 'Количество вхождений', header_format)
                worksheet.write(0, 3, 'Суммарная частотность', header_format)
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


def get_price_segmentation(query: str):
    end_date = time.get_moscow_datetime().date()
    start_date = end_date - datetime.timedelta(days=30)
    params = {'d1': start_date, 'd2': end_date, 'path': query}
    what_to_delete = query.maketrans('', '', string.punctuation)
    query_for_name = query.translate(what_to_delete)
    path_to_excel = \
        f'results/price_segmentation_{query_for_name[0:30]}_{end_date}.xlsx'

    with httpx.Client(timeout=120) as client:
        main_page_response = client.get(MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookies = main_page_response.headers['set-cookie']
        headers = {'cookie': cookies + COOKIES_PART}
        response = client.get(BASE_PRICE_SEGMENTATION_URL, 
                              params=params,
                              headers=headers,
                              follow_redirects=True)
        data = response.json()
        if not data:
            return False
        try:
            workbook = xlsxwriter.Workbook(path_to_excel)
            worksheet = workbook.add_worksheet(name=query_for_name[0:30])
            worksheet.set_column(0, 11, 12)
            header_format = workbook.add_format({'bold': True, 'text_wrap': True, \
                                                'bg_color': '#D9D9D9', 'valign': 'vcenter'})
            bold_format = workbook.add_format({'bold': True})
            percentage_format = workbook.add_format({'num_format': '0.00'})
            worksheet.write(0, 0, 'Диапазон стоимости товара, руб.', header_format)
            worksheet.write(0, 1, 'Товаров, шт.', header_format)
            worksheet.write(0, 2, 'Товаров с продажами, шт.', header_format)
            worksheet.write(0, 3, 'Брендов', header_format)
            worksheet.write(0, 4, 'Брендов с продажами', header_format)
            worksheet.write(0, 5, 'Продавцов', header_format)
            worksheet.write(0, 6, 'Продавцов с продажами', header_format)
            worksheet.write(0, 7, 'Выручка, руб.', header_format)
            worksheet.write(0, 8, 'Продажи, шт.', header_format)
            worksheet.write(0, 9, 'Выручка на товар, руб.', header_format)
            worksheet.write(0, 10, 'Упущенная выручка, руб.', header_format)
            worksheet.write(0, 11, 'Упущенная выручка, %', header_format)
            for row_index, values in enumerate(data, start=1):
                number_of_missed_cols = 0  # сдвиг номера колонки при пропуске
                for col_index, (key, value) in enumerate(values.items()):
                    if not key.endswith('range_price'):
                        col_index -= number_of_missed_cols
                        if key == 'range':
                            worksheet.write(row_index, col_index, value, bold_format)
                        elif key == 'lost_profit_percent':
                            worksheet.write(row_index, col_index, value, percentage_format)
                        else:
                            worksheet.write(row_index, col_index, value)
                    else:
                        number_of_missed_cols += 1
        finally:
            workbook.close()
        return path_to_excel


