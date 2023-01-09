import os
import json


def get_json_cfg(filename):
    p0 = os.path.realpath(__file__)
    cfgfilename = os.path.join(os.path.dirname(p0), filename)
    with open(cfgfilename) as f:
        return json.load(f)


def make_init_json(filename):
    with open('./jsons.py', 'r') as s:
        with open(filename, 'w') as d:
            d.write(s.read())
