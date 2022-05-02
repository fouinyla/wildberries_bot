import httpx
from bs4 import BeautifulSoup
import json
from typing import List

MAIN_PAGE_URL = 'https://mpstats.io/'
BASE_SKU_GETTING_URL = 'https://mpstats.io/wb/bysearch?'

COOKIE_PART = '_ym_uid=1651240592234847018; _ym_d=1651240592; ' \
              '_ga=GA1.1.2054104203.1651240592; _ym_isad=2; ' \
              'supportOnlineTalkID=r85EpoyBIxTRA3agMH9GXs5yZQOApJun; ' \
              '_ym_hostIndex=0-3%2C1-0; _ym_visorc=w; ' \
              'userlogin=a%3A2%3A%7Bs%3A3%3A%22lgn%22%3Bs%3A29%3A%22ip.' \
              'evgeniy.bogdanov%40gmail.com%22%3Bs%3A3%3A%22pwd%22%3Bs%' \
              '3A32%3A%2299fa197de27558f79782ea8373471beb%22%3B%7D; ' \
              '_ga_8S8Y1X62NG=GS1.1.1651240592.1.1.1651240652.0'


def get_sku_html(query: str) -> str:
    with httpx.Client() as client:
        main_page_response = client.get(MAIN_PAGE_URL)
        main_page_response.raise_for_status()
        cookie = main_page_response.headers['set-cookie']
        sku_response = client.get(BASE_SKU_GETTING_URL,
                                  headers={'cookie': cookie + COOKIE_PART},
                                  params={'query': query})
        sku_response.raise_for_status()
        return sku_response.text


def get_sku(query: str) -> List[int]:
    html = get_sku_html(query)
    soup = BeautifulSoup(html, 'lxml')
    tpls = soup.find('wb-search-result')['tpls']
    data = json.loads(tpls)
    return [sku for i, sku in data]
