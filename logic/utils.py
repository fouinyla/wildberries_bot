import json


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
    return d


def get_callback(callback_data):
    return json.loads(callback_data)
