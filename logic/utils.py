import json
from datetime import date
from typing import List, Tuple
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


def get_min_max_week(graph_data: List[typing.Dict], value: str):
    """
    Extracts minimum and maximum date from the graph data received from Mpstats
    value: key from MPSTATS_TRENDS
    """
    min_date, max_date = None, None
    for period in graph_data:
        if MPSTATS_TRENDS[value] in period:
            min_date = date(*map(int, period['end_week'].split('-')))
            break
    for period in reversed(graph_data):
        if MPSTATS_TRENDS[value] in period:
            max_date = date(*map(int, period['end_week'].split('-')))
            break
    return min_date, max_date


def make_graph(graph_data: List[typing.Dict], date_1: date, date_2: date,
               category: str, value: str, view: str):
    """
    value: key from MPSTATS_TRENDS
    view: key from MPSTATS_SECTIONS
    """
    value_english = MPSTATS_TRENDS[value]
    dates = []
    quantities = []
    for period in graph_data:
        week = date(*map(int, period['end_week'].split('-')))
        if not date_1 <= week <= date_2:
            continue
        dates.append(week)
        if value_english in period:
            quantities.append(period[value_english])
        else:
            quantities.append(0)

    fig, ax = plt.subplots()
    ax.plot(dates, quantities)
    ax.set_title(category)
    ax.set_ylabel(value)
    ax.grid(True, axis='both')
    ax.tick_params(axis='x', which='major', labelsize=7, labelrotation=45)

    image_path = f"results/{category.replace('/', '_')}.jpeg"
    fig.savefig(image_path, dpi=1000)
    return image_path
