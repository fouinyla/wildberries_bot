import httpx
import json
from typing import Union


def get_response(url: str) -> httpx.Response:
    return httpx.get(url)


def generate_url(query: str, gender: str = 'common', locale: str = 'ru',
                 lang: str = 'ru') -> str:
    base_api_url = 'https://suggestions.wildberries.ru/api/v2/hint?'
    parameters = f'query={query}&gender={gender}&locale={locale}&lang={lang}'
    return base_api_url + parameters


def get_hints_from_wb(query: str, gender: str = 'common', locale: str = 'ru',
                      lang: str = 'ru') -> Union[list[str], None]:
    url = generate_url(query, gender, locale, lang)
    response = get_response(url)
    if response.status_code == 204:
        return None
    json_array = json.loads(response.text)
    hints = [obj['name'] for obj in json_array if obj['type'] == 'suggest']
    return hints


if __name__ == '__main__':
    print(get_hints_from_wb(''))  # пустой запрос -> [..., ...]
    print(get_hints_from_wb('свитер'))  # одно слово -> [..., ...]
    print(get_hints_from_wb('свитер женский оверсайз с шерстью'))  # конечный запрос -> []

    print(get_hints_from_wb('?><+_'))  # -> None
    print(get_hints_from_wb('abacab'))  # -> None
    print(get_hints_from_wb('ббавмбб'))  # -> None
