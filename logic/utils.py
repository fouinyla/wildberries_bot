import json
from datetime import date
from typing import List
import typing
import matplotlib.pyplot as plt
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
    # print('SIZE', len(d.encode('utf-8')))
    return d


def get_callback(callback_data):
    return json.loads(callback_data)


def make_graph(category: str, value: str, view: str, data: List[typing.Dict],
               date_1: date, date_2: date):
    """
        value: key from MPSTATS_TRENDS
    """
    value_english = MPSTATS_TRENDS[value]
    dates = []
    quantities = []
    for chunk in data:
        week = date(*map(int, chunk['week'].split('-')))
        if not date_1 <= week <= date_2:
            continue
        dates.append(week)
        if value_english in chunk:
            quantities.append(chunk[value_english])
        else:
            quantities.append(0)

    fig, ax = plt.subplots()
    ax.plot(dates, quantities)
    ax.set_title(category)
    ax.set_ylabel(value)
    ax.grid(True, axis='both')
    ax.tick_params(axis='x', which='major', labelsize=10, labelrotation=45)

    image_path = f"results/{category.replace('/', '_')}.jpeg"
    fig.savefig(image_path, dpi=1000)
    return image_path
