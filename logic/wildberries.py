import httpx
from typing import Union


BASE_HINTS_API_URL = 'https://suggestions.wildberries.ru/api/v2/hint?'
BASE_SEARCH_URL = 'https://wbxsearch.wildberries.ru/exactmatch/v2/common?'


def get_response(url: str, params: dict = None) -> httpx.Response:
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response


def get_hints_from_wb(query: str, gender: str = 'common', locale: str = 'ru',
                      lang: str = 'ru') -> Union[list[str], None]:
    response = get_response(BASE_HINTS_API_URL, params={'query': query,
                                                        'gender': gender,
                                                        'locale': locale,
                                                        'lang': lang})
    if response.status_code == 204:
        # print(None)
        return None
    # print([obj['name'] for obj in response.json() if obj['type'] == 'suggest'])
    return [obj['name'] for obj in response.json() if obj['type'] == 'suggest']


def product_exists(query: str) -> bool:
    response = get_response(BASE_SEARCH_URL, params={'query': query})
    json = response.json()
    # print(response.json())
    return bool(json) and 'code' not in json and 't1' not in json['query'] and json['query'] != 'preset=1001'


if __name__ == '__main__':
    print(get_hints_from_wb(''))  # пустой запрос -> [..., ...]
    print(product_exists(''))  # False

    print(get_hints_from_wb('свитер'))  # одно слово -> [..., ...]
    print(product_exists('свитер'))  # True

    print(get_hints_from_wb('свитер женский оверсайз с шерстью'))  # конечный запрос -> []
    print(product_exists('свитер женский оверсайз с шерстью'))  # True

    print(get_hints_from_wb('леденец на палочке большой'))  # конечный запрос -> []
    print(product_exists('леденец на палочке большой'))  # True

    print(get_hints_from_wb('сапожки красные'))  # корректный запрос, но не из хинтов -> 204
    print(product_exists('сапожки красные'))  # True
