from httpx import AsyncClient
from bs4 import BeautifulSoup
from xlsxwriter import Workbook
import datetime
import string
import json
import os
from const.const import *
from .web import request_with_retry, error
from . import time


# создание директории для записи данных
os.makedirs('results', exist_ok=True)


async def get_trends_data(path: str):
    """
        path: 'Детям/Детское питание/Детская смесь' (example)
    """
    async with AsyncClient() as client:
        main_page_response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_MAIN_PAGE_URL)
        if main_page_response is error:
            return error
        cookies = main_page_response.headers.get('set-cookie', '')
        trends_response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_TRENDS_URL,
            params={'view': 'itemsInCategory', 'path': path},
            headers={'cookie': cookies + COOKIES_PART}
        )
    if trends_response is error:
        return error
    if trends_response.status_code != 200:
        return None
    return trends_response.json()


async def get_seo(queries: str):
    flag_all_queries_are_empty = True  # флаг, если все запросы пустые
    queries = queries.split('\n')
    today_date = time.get_moscow_datetime().date()
    async with AsyncClient() as client:
        main_page_response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_MAIN_PAGE_URL)
        if main_page_response is error:
            return error
        cookies = main_page_response.headers.get('set-cookie', '')
        headers = {'cookie': cookies + COOKIES_PART}
        # создание excel-файла для записи данных
        what_to_delete = queries[0].maketrans('', '', string.punctuation)
        query_for_tablename = queries[0].translate(what_to_delete)
        if not query_for_tablename:
            query_for_tablename = 'символьный_запрос'
        path_to_excel = f'results/SEO_{query_for_tablename[0:30]}_{today_date}.xlsx'

        with Workbook(path_to_excel) as workbook:
            for num, query in enumerate(queries, start=1):
                # запрос на получение html с SKU
                sku_response = await request_with_retry(
                    client=client,
                    method='GET',
                    url=MPSTATS_SKU_URL,
                    headers=headers,
                    params={'query': query}
                )
                if sku_response is error:
                    return error
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
                response = await request_with_retry(
                    client=client,
                    method='POST',
                    url=MPSTATS_SEO_URL,
                    headers=headers,
                    data=data
                )
                if response is error:
                    return error
                result = response.json().get('result', [])
                # создание страницы в excel-файле с названиями колонок
                what_to_delete = query.maketrans('', '', string.punctuation)
                query_for_worksheet = query.translate(what_to_delete)
                query_for_worksheet = query_for_worksheet[0:28] + str(num)
                if not query_for_worksheet:
                    query_for_worksheet = 'Символьный запрос'
                worksheet = workbook.add_worksheet(name=query_for_worksheet)
                worksheet.set_column(0, 3, 15)
                worksheet.set_column(1, 1, 90)
                header_format = workbook.add_format({'bold': True, 'text_wrap': True,
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
    return path_to_excel, flag_all_queries_are_empty


async def get_price_segmentation(query: str):
    end_date = time.get_moscow_datetime().date()
    start_date = end_date - datetime.timedelta(days=30)
    params = {'d1': start_date, 'd2': end_date, 'path': query}
    what_to_delete = query.maketrans('', '', string.punctuation)
    query_for_name = query.translate(what_to_delete)
    path_to_excel = f'results/price_segmentation_{query_for_name[0:30]}_{end_date}.xlsx'

    async with AsyncClient() as client:
        main_page_response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_MAIN_PAGE_URL)
        if main_page_response is error:
            return error
        cookies = main_page_response.headers.get('set-cookie', '')
        headers = {'cookie': cookies + COOKIES_PART}
        response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_PRICE_SEGMENTATION_URL,
            params=params,
            headers=headers
        )
        if response is error:
            return error
        if response.status_code != 200 or not response.json():
            return False
        data = response.json()
        with Workbook(path_to_excel) as workbook:
            worksheet = workbook.add_worksheet(name=query_for_name[0:30])
            worksheet.set_column(0, 12, 12)
            header_format = workbook.add_format({'bold': True,
                                                 'text_wrap': True,
                                                 'bg_color': '#D9D9D9',
                                                 'valign': 'vcenter'})
            bold_format = workbook.add_format({'bold': True})
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
            worksheet.write(0, 10, 'Потенциальная выручка, руб.', header_format)
            worksheet.write(0, 11, 'Упущенная выручка, руб.', header_format)
            worksheet.write(0, 12, 'Упущенная выручка, %', header_format)
            for row_index, values in enumerate(data, start=1):
                number_of_missed_cols = 0  # сдвиг номера колонки при пропуске
                for col_index, (key, value) in enumerate(values.items()):
                    if not key.endswith('range_price'):
                        col_index -= number_of_missed_cols
                        if key == 'range':
                            worksheet.write(row_index, col_index, value, bold_format)
                        else:
                            worksheet.write(row_index, col_index, value)
                    else:
                        number_of_missed_cols += 1
        return path_to_excel


async def get_card_data(article: str):
    end_date = time.get_moscow_datetime().date()
    start_date = end_date - datetime.timedelta(days=30)
    async with AsyncClient() as client:
        main_page_response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_MAIN_PAGE_URL)
        if main_page_response is error:
            return error
        cookies = main_page_response.headers.get('set-cookie', '')
        headers = {'cookie': cookies + COOKIES_PART}
        params = {'d1': start_date, 'd2': end_date}
        response = await request_with_retry(
            client=client,
            method='GET',
            url=MPSTATS_SALES_URL.replace('ARTICLE', article),
            headers=headers,
            params=params)
    if response is error:
        return error
    if response.status_code != 200:
        return False
    return response.json()
