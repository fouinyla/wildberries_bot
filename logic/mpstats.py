from tokenize import Triple
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
        # тестовая строка (mock)
        #data = [{"range":"3-553","items":34984,"items_with_sells":16329,"brands":2935,"brands_with_sells":2194,"sellers":2759,"sellers_with_sells":2237,"revenue":237149402,"sales":779911,"product_revenue":14523,"min_range_price":3,"max_range_price":553,"lost_profit":206264130,"lost_profit_percent":21.573371429423112},{"range":"553-817","items":34946,"items_with_sells":11459,"brands":2724,"brands_with_sells":1714,"sellers":2445,"sellers_with_sells":1767,"revenue":243528274,"sales":379620,"product_revenue":21252,"min_range_price":554,"max_range_price":817,"lost_profit":191486480,"lost_profit_percent":14.101259334276845},{"range":"817-941","items":41153,"items_with_sells":5121,"brands":1640,"brands_with_sells":1017,"sellers":1509,"sellers_with_sells":1035,"revenue":130945533,"sales":162316,"product_revenue":25570,"min_range_price":818,"max_range_price":941,"lost_profit":111662085,"lost_profit_percent":6.066597712248766},{"range":"941-1099","items":28805,"items_with_sells":5919,"brands":1828,"brands_with_sells":1185,"sellers":1798,"sellers_with_sells":1221,"revenue":210393654,"sales":230222,"product_revenue":35545,"min_range_price":942,"max_range_price":1099,"lost_profit":160039937,"lost_profit_percent":9.491898296642283},{"range":"1099-1405","items":34876,"items_with_sells":10139,"brands":2547,"brands_with_sells":1608,"sellers":2451,"sellers_with_sells":1657,"revenue":331109347,"sales":290019,"product_revenue":32657,"min_range_price":1100,"max_range_price":1405,"lost_profit":306851579,"lost_profit_percent":12.649068501074453},{"range":"1405-1762","items":34933,"items_with_sells":12122,"brands":2439,"brands_with_sells":1597,"sellers":2372,"sellers_with_sells":1664,"revenue":420481818,"sales":290608,"product_revenue":34687,"min_range_price":1406,"max_range_price":1762,"lost_profit":395874721,"lost_profit_percent":15.583869245350208},{"range":"1762-2150","items":35015,"items_with_sells":12093,"brands":2315,"brands_with_sells":1489,"sellers":2206,"sellers_with_sells":1542,"revenue":497071195,"sales":276123,"product_revenue":41104,"min_range_price":1763,"max_range_price":2150,"lost_profit":471537539,"lost_profit_percent":15.580682812955656},{"range":"2150-2447","items":53505,"items_with_sells":7457,"brands":1791,"brands_with_sells":1128,"sellers":1698,"sellers_with_sells":1170,"revenue":393666154,"sales":184869,"product_revenue":52791,"min_range_price":2151,"max_range_price":2447,"lost_profit":320832249,"lost_profit_percent":6.375877102099282},{"range":"2447-2599","items":22666,"items_with_sells":3521,"brands":1186,"brands_with_sells":708,"sellers":1163,"sellers_with_sells":768,"revenue":251034167,"sales":105399,"product_revenue":71296,"min_range_price":2448,"max_range_price":2599,"lost_profit":181366502,"lost_profit_percent":7.043349740465497},{"range":"2599-2799","items":58802,"items_with_sells":3946,"brands":1254,"brands_with_sells":784,"sellers":1226,"sellers_with_sells":813,"revenue":264830156,"sales":105398,"product_revenue":67113,"min_range_price":2600,"max_range_price":2799,"lost_profit":185723330,"lost_profit_percent":3.0763335467737694},{"range":"2799-2878","items":4726,"items_with_sells":1414,"brands":697,"brands_with_sells":421,"sellers":672,"sellers_with_sells":428,"revenue":83952207,"sales":31727,"product_revenue":59372,"min_range_price":2800,"max_range_price":2878,"lost_profit":71542633,"lost_profit_percent":12.553358847448878},{"range":"2878-3099","items":59647,"items_with_sells":4529,"brands":1286,"brands_with_sells":801,"sellers":1248,"sellers_with_sells":835,"revenue":262564522,"sales":96199,"product_revenue":57974,"min_range_price":2879,"max_range_price":3099,"lost_profit":223082357,"lost_profit_percent":3.2581178688238923},{"range":"3099-3278","items":10282,"items_with_sells":2599,"brands":999,"brands_with_sells":593,"sellers":970,"sellers_with_sells":629,"revenue":135694959,"sales":46528,"product_revenue":52210,"min_range_price":3100,"max_range_price":3278,"lost_profit":144243409,"lost_profit_percent":11.669295433979197},{"range":"3278-3824","items":41933,"items_with_sells":7089,"brands":1640,"brands_with_sells":1010,"sellers":1609,"sellers_with_sells":1079,"revenue":447150082,"sales":137466,"product_revenue":63076,"min_range_price":3279,"max_range_price":3824,"lost_profit":411194922,"lost_profit_percent":7.575257216740092},{"range":"3824-4408","items":27941,"items_with_sells":5676,"brands":1497,"brands_with_sells":862,"sellers":1459,"sellers_with_sells":908,"revenue":408909776,"sales":108038,"product_revenue":72041,"min_range_price":3825,"max_range_price":4408,"lost_profit":457267555,"lost_profit_percent":9.682592045661423},{"range":"4408-4749","items":61302,"items_with_sells":2835,"brands":1010,"brands_with_sells":540,"sellers":955,"sellers_with_sells":575,"revenue":212752185,"sales":50681,"product_revenue":75044,"min_range_price":4409,"max_range_price":4749,"lost_profit":215169017,"lost_profit_percent":2.2129038984471783},{"range":"4749-4913","items":8588,"items_with_sells":1301,"brands":670,"brands_with_sells":333,"sellers":648,"sellers_with_sells":349,"revenue":115219131,"sales":25697,"product_revenue":88561,"min_range_price":4750,"max_range_price":4913,"lost_profit":115262821,"lost_profit_percent":7.876258074968105},{"range":"4913-5900","items":35098,"items_with_sells":6093,"brands":1418,"brands_with_sells":785,"sellers":1355,"sellers_with_sells":836,"revenue":521261793,"sales":107044,"product_revenue":85550,"min_range_price":4914,"max_range_price":5900,"lost_profit":563851869,"lost_profit_percent":8.699244599593172},{"range":"5900-7080","items":34802,"items_with_sells":4795,"brands":1211,"brands_with_sells":633,"sellers":1127,"sellers_with_sells":658,"revenue":400157788,"sales":69532,"product_revenue":83453,"min_range_price":5901,"max_range_price":7080,"lost_profit":538829360,"lost_profit_percent":7.265886768126768},{"range":"7080-8595","items":34916,"items_with_sells":3615,"brands":986,"brands_with_sells":503,"sellers":925,"sellers_with_sells":524,"revenue":255395726,"sales":36065,"product_revenue":70648,"min_range_price":7081,"max_range_price":8595,"lost_profit":404679892,"lost_profit_percent":5.624617093446626},{"range":"8596-10710","items":35006,"items_with_sells":2970,"brands":911,"brands_with_sells":433,"sellers":800,"sellers_with_sells":448,"revenue":230454148,"sales":26406,"product_revenue":77593,"min_range_price":8596,"max_range_price":10710,"lost_profit":460318531,"lost_profit_percent":4.8797535329347435},{"range":"10710-13799","items":34893,"items_with_sells":2400,"brands":780,"brands_with_sells":345,"sellers":651,"sellers_with_sells":334,"revenue":157306810,"sales":14662,"product_revenue":65544,"min_range_price":10711,"max_range_price":13799,"lost_profit":402831291,"lost_profit_percent":4.009026352613396},{"range":"13799-19082","items":34940,"items_with_sells":1934,"brands":671,"brands_with_sells":271,"sellers":563,"sellers_with_sells":270,"revenue":167752508,"sales":11666,"product_revenue":86738,"min_range_price":13800,"max_range_price":19082,"lost_profit":439239411,"lost_profit_percent":3.3555660635623816},{"range":"19082-32600","items":34950,"items_with_sells":1327,"brands":557,"brands_with_sells":190,"sellers":432,"sellers_with_sells":190,"revenue":97091998,"sales":4875,"product_revenue":73166,"min_range_price":19084,"max_range_price":32600,"lost_profit":407333773,"lost_profit_percent":2.281022578839335},{"range":"32600-626230","items":34928,"items_with_sells":359,"brands":358,"brands_with_sells":92,"sellers":263,"sellers_with_sells":83,"revenue":34274190,"sales":1036,"product_revenue":95471,"min_range_price":32602,"max_range_price":626230,"lost_profit":143743097,"lost_profit_percent":0.5899091796291506}]
        try:
            workbook = xlsxwriter.Workbook(path_to_excel)
            worksheet = workbook.add_worksheet(name=query_for_name)
            worksheet.write(0, 0, 'Диапазон стоимости товара, руб.')
            worksheet.write(0, 1, 'Товаров, шт.')
            worksheet.write(0, 2, 'Товаров с продажами, шт.')
            worksheet.write(0, 3, 'Брендов')
            worksheet.write(0, 4, 'Брендов с продажами')
            worksheet.write(0, 5, 'Продавцов')
            worksheet.write(0, 6, 'Продавцов с продажами')
            worksheet.write(0, 7, 'Выручка, руб.')
            worksheet.write(0, 8, 'Продажи, шт.')
            worksheet.write(0, 9, 'Выручка на товар, руб.')
            worksheet.write(0, 10, 'Упущенная выручка, руб.')
            worksheet.write(0, 11, 'Упущенная выручка, %')
            for row_index, values in enumerate(data, start=1):
                number_of_missed_cols = 0  # сдвиг номера колонки при пропуске
                for col_index, (key, value) in enumerate(values.items()):
                    if not key.endswith('range_price'):
                        col_index -= number_of_missed_cols
                        worksheet.write(row_index, col_index, value)
                    else:
                        number_of_missed_cols += 1
        finally:
            workbook.close()
        return path_to_excel


