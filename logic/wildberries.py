import httpx
from typing import Union, List
from const.const import *


def get_hints(query: str, gender: str = 'common', locale: str = 'ru',
              lang: str = 'ru') -> Union[List[str], None]:
    """
        Returns a list of Wildberries hints for the given query
    """
    response = httpx.get(WB_HINTS_URL, params={'query': query,
                                               'gender': gender,
                                               'locale': locale,
                                               'lang': lang})
    response.raise_for_status()
    if response.status_code == 204:
        return None
    return [obj['name'] for obj in response.json() if obj['type'] == 'suggest']


def product_exists(query: str) -> bool:
    """
        Checks if there are products on Wildberries for the given query
    """
    response = httpx.get(WB_SEARCH_URL, params={'query': query})
    response.raise_for_status()
    json = response.json()
    return (bool(json)
            and json['query'] != 'preset=1001'
            and ('t1' not in json['query']
            or 't2' in json['query']))


def get_page_url(query):
    for page in range(1, 10000):
        url = 'https://wbxsearch.wildberries.ru/exactmatch/v3/common?' \
            'appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,' \
            f'-102269,-1278703,-1255563&emp=0&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&' \
            f'query={query}&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,48,22,' \
            '1,66,31,40,71&resultset=catalog&sort=popular&spp=0&stores=117673,122258,122259,125238,' \
            '125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043'
        yield url


def search_for_article(article, query):
    card_counter = 3
    page_counter = 0
    for url in get_page_url(query):
        response = httpx.get(url=url)
        page_counter += 1
        if not response.json():
            return None
        card_list = response.json()['catalog']['data']['products']
        for card in card_list:
            if card['id'] == article:
                return page_counter, card_counter
            card_counter += 1

