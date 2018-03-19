__author__ = 'oidin'

import json
import re
import argparse

def openConfigFile(filename):
    data = []
    with open(filename) as data_file:
        data = json.load(data_file)
    return data


config_info = []
config_info = openConfigFile("gateway_config.json")

def unicodeToStr(name):
    string = name.encode('ascii','ignore')
    return string

m = argparse.ArgumentParser()
m.add_argument("--search","-s",type=str,default='',help="Try something like 'V4.*u.*RB'. In addition you can read http://pers.narod.ru/phps/php_regexp.html")
args = m.parse_args()
pattern = re.compile("")
if (args.search):
    pattern = re.compile(args.search)

for connection in config_info:
    channel = unicodeToStr(connection["channel"])
    pv = unicodeToStr(connection["pv"])
    if not (pattern.search(channel) or pattern.search(pv)):
        continue
    direction = "<->"
    if connection["direction"]=="p":
        direction = "<-"
    elif connection["direction"]=="x":
        direction = "->"
    print channel+" "+direction+" "+pv
