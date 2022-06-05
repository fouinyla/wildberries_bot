import httpx
from bs4 import BeautifulSoup
import json
import xlsxwriter
from . import time
import os
import datetime
from typing import Tuple, List, Dict, Optional
import string
from const.const import *
import matplotlib.pyplot as plt
import math


# создание директории для записи данных
os.makedirs('results', exist_ok=True)


async def get_trends_data(path: str, view: str) -> Optional[List[Dict]]:
    """
        path: 'Детям/Детское питание/Детская смесь' (example)
        view: key from MPSTATS_SECTIONS
    """
    async with httpx.AsyncClient(timeout=60) as client:
        main_page_response = await client.get(MPSTATS_MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookie = main_page_response.headers['set-cookie']
        trends_response = await client.get(
            MPSTATS_TRENDS_URL,
            headers={'cookie': cookie + COOKIES_PART},
            params={'view': MPSTATS_SECTIONS[view], 'path': path},
            follow_redirects=True)
    if trends_response.status_code != 200 or not trends_response.json():
        return None
    print(trends_response.json())
    return trends_response.json()


async def get_seo(queries: str) -> Tuple[str, bool]:
    flag_all_queries_are_empty = True  # флаг, если все запросы пустые
    queries = queries.split('\n')
    today_date = time.get_moscow_datetime().date()
    async with httpx.AsyncClient(timeout=60) as client:
        # получение кук для отправки запроса для получения SKU
        main_page_response = await client.get(MPSTATS_MAIN_PAGE_URL)
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
                sku_response = await client.get(MPSTATS_SKU_URL,
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
                response = await client.post(MPSTATS_SEO_URL,
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
        finally:
            workbook.close()
    return path_to_excel, flag_all_queries_are_empty


async def get_price_segmentation(query: str):
    end_date = time.get_moscow_datetime().date()
    start_date = end_date - datetime.timedelta(days=30)
    params = {'d1': start_date, 'd2': end_date, 'path': query}
    what_to_delete = query.maketrans('', '', string.punctuation)
    query_for_name = query.translate(what_to_delete)
    path_to_excel = \
        f'results/price_segmentation_{query_for_name[0:30]}_{end_date}.xlsx'

    async with httpx.AsyncClient(timeout=60) as client:
        main_page_response = await client.get(MPSTATS_MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookies = main_page_response.headers['set-cookie']
        headers = {'cookie': cookies + COOKIES_PART}
        response = await client.get(MPSTATS_PRICE_SEGMENTATION_URL,
                                    params=params,
                                    headers=headers,
                                    follow_redirects=True)
        if response.status_code != 200 or not response.json():
            return False
        data = response.json()
        try:
            workbook = xlsxwriter.Workbook(path_to_excel)
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
        finally:
            workbook.close()
        return path_to_excel


async def plot_month_sales_graph(article: str) -> Tuple[str, bool]:
    end_date = time.get_moscow_datetime().date()
    start_date = end_date - datetime.timedelta(days=30)
    async with httpx.AsyncClient(timeout=60) as client:
        # получение кук для отправки запроса для получения SKU
        main_page_response = await client.get(MPSTATS_MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookies = main_page_response.headers['set-cookie']
        headers = {'cookie': cookies + COOKIES_PART}

        params = {'d1': start_date, 'd2': end_date}
        response = await client.get(MPSTATS_SALES_URL.replace('ARTICLE', article),
                                        headers=headers,
                                        params=params,
                                        follow_redirects=True)
        if response.status_code != 200:
            return False
        graph_data = response.json()
    # построение графиков
    fig, ax1 = plt.subplots()
    color1 = '#FF4D29'
    ax1.plot(graph_data['days'], graph_data['sales'], color=color1)
    ax1.set_ylabel('Продажи', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, axis='both')

    ax2 = ax1.twinx()
    color2 = '#3870F5'
    ax2.plot(graph_data['days'], graph_data['balance'], color=color2)
    ax2.set_ylabel('Остатки', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    #ax2.grid(True, axis='y')

    ax1.set_title(f'Продажи и остатки за месяц для артикула {article}')
    ax1.tick_params(axis='x', which='major', labelsize=7, labelrotation=45)
    # сохранение
    image_path = f"results/month_sales_for_{article}.jpeg"
    fig.savefig(image_path, dpi=1000)
    return image_path