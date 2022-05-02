import httpx
from typing import Union, List

BASE_HINTS_API_URL = 'https://suggestions.wildberries.ru/api/v2/hint?'
BASE_SEARCH_URL = 'https://wbxsearch.wildberries.ru/exactmatch/v2/common?'


def get_response(url: str, params: dict = None) -> httpx.Response:
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response


def get_hints(query: str, gender: str = 'common', locale: str = 'ru',
              lang: str = 'ru') -> Union[List[str], None]:
    """
        Returns a list of Wildberries hints for the given query
    """
    response = get_response(BASE_HINTS_API_URL, params={'query': query,
                                                        'gender': gender,
                                                        'locale': locale,
                                                        'lang': lang})
    if response.status_code == 204:
        return None
    return [obj['name'] for obj in response.json() if obj['type'] == 'suggest']


def product_exists(query: str) -> bool:
    """
        Checks if there are products on Wildberries for the given query
    """
    response = get_response(BASE_SEARCH_URL, params={'query': query})
    json = response.json()
    return (bool(json)
            and json['query'] != 'preset=1001'
            and ('t1' not in json['query']
            or 't2' in json['query']))
