import json
from datetime import date
from typing import List
import typing
import matplotlib as plt
from const.const import MPSTATS_TRENDS

# using:
# d = Dict(
#   first="hello"
# )
# d.second = 5
# print(d.first, d.second)


class Dict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__getitem__


def callback(data):
    d = json.dumps(data)
    print('SIZE', len(d.encode('utf-8')))
    return d


def get_callback(callback_data):
    return json.loads(callback_data)


def make_graph(value: str, data: List[typing.Dict], date_1: date, date_2: date,
               header: str):
    """
        value: key from TRENDS_VALUES
    """
    value_english = MPSTATS_TRENDS[value]
    dates = []
    quantities = []
    for chunk in data:
        week = date(*map(int, chunk['week'].split('-')))
        if not date_1 <= week <= date_2:
            continue
        dates.append(chunk['week'])
        quantities.append(chunk[value_english])

    plt.plot(dates, quantities)
    plt.title(header)
    plt.ylabel(value)
    plt.grid(True, axis='both')
    plt.xticks(fontsize=5, rotation=90)

    image_path = f'results/{header}.jpeg'
    plt.savefig(image_path, dpi=1000)
    return image_path
