import json
from datetime import date
from typing import List
import typing
import matplotlib.pyplot as plt
from const.const import *
from xlsxwriter import Workbook
from random import randint
import re


# using:
# d = Dict(
#   first="hello"
# )
# d.second = 5
# print(d.first, d.second)


class Dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__getitem__


def callback(data):
    d = json.dumps(data)
    # print('SIZE', len(d.encode('utf-8')))
    return d


def get_callback(callback_data):
    return json.loads(callback_data)


def get_min_max_week(graph_data: List[typing.Dict], value: str):
    """
    Extracts minimum and maximum date from the graph data received from Mpstats
    value: key from MPSTATS_TRENDS
    """
    min_date, max_date = None, None
    for period in graph_data:
        if MPSTATS_TRENDS[value] in period:
            min_date = date(*map(int, period['end_week'].split('-')))
            break
    for period in reversed(graph_data):
        if MPSTATS_TRENDS[value] in period:
            max_date = date(*map(int, period['end_week'].split('-')))
            break
    return min_date, max_date


def validate_trand_graph_date(text: str, min_date: date, max_date: date) -> bool:
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', text):
        return False
    user_date = date(*map(int, text.split('-')))
    if min_date <= user_date <= max_date:
        return True
    return False


def make_trand_graph(graph_data: List[typing.Dict], date_1: date, date_2: date,
                     category: str, value: str):
    """
    value: key from MPSTATS_TRENDS
    """
    value_english = MPSTATS_TRENDS[value]
    dates = []
    quantities = []
    for period in graph_data:
        week = date(*map(int, period['end_week'].split('-')))
        if not date_1 <= week <= date_2:
            continue
        dates.append(week)
        quantities.append(period[value_english])

    fig, ax = plt.subplots()
    ax.plot(dates, quantities)
    ax.set_title(category)
    ax.set_ylabel(value)
    ax.grid(True, axis='both')
    ax.tick_params(axis='x', which='major', labelsize=7, labelrotation=45)

    image_path = f"results/trand_graph_{category.replace('/', '_')}_{randint(1, 1000)}.jpeg"
    fig.savefig(image_path, dpi=1000)
    return image_path


def plot_month_sales_graph(graph_data: typing.Dict, article: str):
    # построение графиков
    fig, ax1 = plt.subplots()
    color1 = '#FF4D29'
    ax1.plot(graph_data['days'], graph_data['sales'], color=color1)
    ax1.set_ylabel('Продажи', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1, color=color1)
    ax1.grid(True, axis='both')

    ax2 = ax1.twinx()
    color2 = '#3870F5'
    ax2.plot(graph_data['days'], graph_data['balance'], color=color2)
    ax2.set_ylabel('Остатки', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2, color=color2)
    
    ax3 = ax1.twinx()
    color3 = 'g'
    ax3.plot(graph_data['days'], graph_data['final_price'], color=color3)
    ax3.set_ylabel('Цена', color=color3)
    ax3.tick_params(axis='y', labelcolor=color3, color=color3, pad=45, labeltop=True)

    ax1.set_title(f'Данные по товару за месяц для артикула {article}')
    ax1.tick_params(axis='x', which='major', labelsize=7, labelrotation=45)
    # сохранение
    image_path = f"results/month_sales_for_{article}.jpeg"
    fig.savefig(image_path, dpi=1000, bbox_inches='tight')

    # расчет доп. значений
    start_day = graph_data['days'][0]
    end_day = graph_data['days'][-1]
    total_sales = sum(graph_data['sales'])
    balance_at_the_end = graph_data['balance'][-1]
    return dict(
                image_path=image_path,
                start_day=start_day,
                end_day=end_day,
                total_sales=total_sales,
                balance_at_the_end=balance_at_the_end
                )


def create_queries_table(card_data: typing.Dict, article: str):
    queries = tuple(filter(lambda query: query[1]['count'] > 4, card_data['words'].items()))
    queries = sorted(queries, key=lambda query: query[1]['count'], reverse=True)
    path_to_excel = f'results/search_queries_for_{article}.xlsx'
    with Workbook(path_to_excel) as workbook:
        worksheet = workbook.add_worksheet(name=f'артикул={article}')
        worksheet.set_column(0, 0, 40)
        worksheet.set_column(1, 3, 11)
        header_format = workbook.add_format({'bold': True,
                                             'text_wrap': True,
                                             'bg_color': '#D9D9D9',
                                             'valign': 'vcenter'})
        #bold_format = workbook.add_format({'bold': True})
        worksheet.write(0, 0, 'Ключевое слово', header_format)
        worksheet.write(0, 1, 'Частотность запроса', header_format)
        worksheet.write(0, 2, 'Всего результатов', header_format)
        worksheet.write(0, 3, 'Средняя позиция', header_format)
        for column, day in enumerate(card_data['days'], start=4):  
            worksheet.write(0, column, day, header_format)
            worksheet.set_column(column, column, 5)
        for row, (query, data) in enumerate(queries, start=1):
            worksheet.write(row, 0, query)
            worksheet.write(row, 1, data['count'])
            worksheet.write(row, 2, data['total'])
            worksheet.write(row, 3, data['avgPos'])
            for column, number in enumerate(data['pos'], start=4):
                if str(number) == 'NaN':
                    number = '-'
                worksheet.write(row, column, number)
    return path_to_excel
