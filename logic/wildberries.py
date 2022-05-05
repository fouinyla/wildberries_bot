import httpx
from typing import Union, List
from const.const import *


def get_hints(query: str, gender: str = 'common', locale: str = 'ru',
              lang: str = 'ru') -> Union[List[str], None]:
    """
        Returns a list of Wildberries hints for the given query
    """
    response = httpx.get(BASE_WB_HINTS_API_URL, params={'query': query,
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
    response = httpx.get(BASE_WB_SEARCH_URL, params={'query': query})
    response.raise_for_status()
    json = response.json()
    return (bool(json)
            and json['query'] != 'preset=1001'
            and ('t1' not in json['query']
            or 't2' in json['query']))
