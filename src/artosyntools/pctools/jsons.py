import os
import json


def get_user_pass(js: json) -> list[dict]:
    configs = []
    lgs = js['p301d']['login']
    for lg in lgs:
        configs += [{'username': lg[0], 'password': lg[1]}]
    return configs


def make_init_json(filename):
    with open('./jsons.py', 'r') as s:
        with open(filename, 'w') as d:
            d.write(s.read())
