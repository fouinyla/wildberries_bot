import logging
from httpx import AsyncClient
from const.const import *
from .web import request_with_retry, error


async def get_hints(query: str, gender: str = 'common', locale: str = 'ru',
                    lang: str = 'ru'):
    """
        Returns a list of Wildberries hints for the given query
    """
    async with AsyncClient() as client:
        response = await request_with_retry(
            client=client,
            method='GET',
            url=WB_HINTS_URL,
            params={'query': query,
                    'gender': gender,
                    'locale': locale,
                    'lang': lang}
        )
    if response is error:
        return error
    if response.status_code == 204:
        return None
    return [obj['name'] for obj in response.json() if obj['type'] == 'suggest']


def get_page_url(query):
    for page in range(1, 10000):
        url = 'https://wbxsearch.wildberries.ru/exactmatch/v3/common?' \
            'appType=1&couponsGeo=12,3,18,15,21&curr=rub&dest=-1029256,' \
            f'-102269,-1278703,-1255563&emp=0&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&' \
            f'query={query}&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,48,22,' \
            '1,66,31,40,71&resultset=catalog&sort=popular&spp=0&stores=117673,122258,122259,125238,' \
            '125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043'
        yield url


async def search_for_article(article, query):
    card_counter = 3
    page_counter = 0
    async with AsyncClient() as client:
        for url in get_page_url(query):
            page_counter += 1
            response = await request_with_retry(
                client=client,
                method='GET',
                url=url)
            if response is error:
                return error
            if not response.json():
                return None
            card_list = response.json().get('catalog', {}).get('data', {}).get('products', [])
            for card in card_list:
                if card['id'] == article:
                    return page_counter, card_counter
                card_counter += 1


async def find_the_card(article, APIkey, supplierID):
    headers = {
        'accept': 'application/json',
        'Authorization': APIkey,
        'Content-type': 'application/json'
    }
    data_list = {
        'id': 1,
        'jsonrpc': '2.0',
        'params': {
            'filter': {
                'find': [{
                    'column': 'nomenclatures.nmId',
                    'search': article
                }]
            },
            'query': {
                'limit': 1,
                'offset': 0,
                'total': 0
            },
            'supplierID': supplierID,
            'isArchive': True,
            'withError': False
        }
    }
    async with AsyncClient() as client:
        response = await request_with_retry(
            client=client,
            method='POST',
            url=WB_CARD_SEARCH_URL,
            headers=headers,
            json=data_list)
    if response is error:
        return error
    cards = response.json().get('result', {}).get('cards', [])
    return None if not cards else cards[0]


async def rename_the_card(new_name, article, APIkey, supplierID):
    headers = {
        'accept': 'application/json',
        'Authorization': APIkey,
        'Content-type': 'application/json'
    }
    data = {
        'id': 1,
        'jsonrpc': '2.0',
        'params': {
            'card': {}
        }
    }
    card = await find_the_card(article, APIkey, supplierID)
    if card is error:
        return error
    data['params']['card'] = card
    logging.info("Card: ", card)
    if card:
        data['params']['card']['addin'][1]['params'][0]['value'] = new_name
        async with AsyncClient() as client:
            response = await request_with_retry(
                client=client,
                method='POST',
                url=WB_CARD_UPDATE_URL,
                headers=headers,
                json=data)
        if response is error:
            return error
        return True
    return False
