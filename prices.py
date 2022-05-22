import json
from const.const import *


def get_price_categories(category_name: str):
    with open('json_categories/cats.min.json') as file:
        categories_json = json.load(file)
        if not '/' in category_name:
            second_layer = list(
                filter(lambda category: category['name'] == category_name,
                        categories_json)
            )
            categories = [category['name'] for category in second_layer[0]['childs']]
        else:
            first_layer_name, second_layer_name = category_name.split('/')
            second_layer = list(
                filter(lambda category: category['name'] == first_layer_name,
                        categories_json)
            )
            third_layer = list(
                filter(lambda category: category['name'] == second_layer_name,
                        second_layer[0]['childs'])
            )
            categories = [category['name'] for category in third_layer[0]['childs']]
    return categories

print(get_price_categories('Детям'))
print(get_price_categories('Детям/Школа'))
