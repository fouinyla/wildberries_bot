import httpx
from typing import Union, List
from const.const import *


async def get_hints(query: str, gender: str = 'common', locale: str = 'ru',
                    lang: str = 'ru') -> Union[List[str], None]:
    """
        Returns a list of Wildberries hints for the given query
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(WB_HINTS_URL, params={'query': query,
                                                          'gender': gender,
                                                          'locale': locale,
                                                          'lang': lang})
    response.raise_for_status()
    if response.status_code == 204:
        return None
    return [obj['name'] for obj in response.json() if obj['type'] == 'suggest']


async def product_exists(query: str) -> bool:
    """
        Checks if there are products on Wildberries for the given query
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(WB_SEARCH_URL, params={'query': query})
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


async def search_for_article(article, query):
    card_counter = 3
    page_counter = 0
    async with httpx.AsyncClient() as client:
        for url in get_page_url(query):
            response = await client.get(url=url)
            page_counter += 1
            if not response.json():
                return None
            card_list = response.json()['catalog']['data']['products']
            for card in card_list:
                if card['id'] == article:
                    return page_counter, card_counter
                card_counter += 1


async def find_the_card(article, APIkey, supplierID):
    headers = {
        "accept": "*/*",
        "Authorization": APIkey,
        "Content-type": "application/json"
    }
    data_list = {
        "id": 1,
        "jsonrpc": "2.0",
        "params": {
            "filter": {
                "find": [{
                    "column": "nomenclatures.nmId",
                    "search": article
                }]
            },
            "query": {
                "limit": 1,
                "offset": 0,
                "total": 0
            },
            "supplierID": supplierID,
            "isArchive": True,
            "withError": False
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("https://suppliers-api.wildberries.ru/card/list", headers=headers, json=data_list)
        if response.status_code == 200:
            return response.json()["result"]["cards"][0]
        else:
            return None


async def rename_the_card(new_name, article, APIkey, supplierID):
    headers = {
        "accept": "*/*",
        "Authorization": APIkey,
        "Content-type": "application/json"
    }
    data = {
        "id": 1,
        "jsonrpc": "2.0",
        "params": {
            "card": {}
        }
    }
    async with httpx.AsyncClient() as client:
        data["params"]["card"] = await find_the_card(article, APIkey, supplierID)
        if data["params"]["card"]:
            data["params"]["card"]["addin"][1]["params"][0]["value"] = new_name
            await client.post("https://suppliers-api.wildberries.ru/card/update", headers=headers, json=data)
            return True
        else:
            return None
