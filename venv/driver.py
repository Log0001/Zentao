# -- encoding:utf-8 --

import requests
import json
import re


def driver_goto_page(response_ses, url):
    response = response_ses.get(url)
    return response


def get_json_data(dirs):
    with open(dirs) as file:
        data = json.loads(file.read())
        return data


def save_file(filename, data):
    with open(filename, 'w') as file:
        file.write(data)


def read_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return data


def get_productid(data):
    print("productid")
    print(data)
    productid_re = re.match('^<li(.*?)productid="(.*?)">', data)
    if productid_re:
        productid = productid_re.group(2)
    print(productid)
    return productid


def get_productname(data):
    productname_re = re.search('<a(.*?):;" title="(.*?)">(.*?)</a>', data)
    if productname_re:
        productname = productname_re.group(3)
    return productname