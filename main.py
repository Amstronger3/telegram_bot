import json
import os
from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
import requests

import config


def check_valid_currency_name(name):
    if len(name) != 3:
        print(0)
        return "Length of name currency must be 3 symbols only!"
    elif not name.upper() in config.currency_list:
        print(1)
        return "Invalid name of currency! \nExample: USD, EUR, UAH"


def make_request_to_convert(currency_to, amount=10, currency_from="USD"):
    url_convert = f"https://v1.nocodeapi.com/aleksandr/cx/xLCfYxTcwgugBexS/rates/convert?amount={str(amount)}&from={currency_from}&to={currency_to}"
    response = requests.get(url_convert)
    return round(response.json()["result"], 2)


def make_request_to_get_graph_for_7_day(base_currency_graph="USD", req_currency_graph="CAD"):
    start_date = datetime.date(datetime.now()) - timedelta(days=7)
    end_date = datetime.date(datetime.now())
    url_history = f"{config.base_url}timeseries?start_date={str(start_date)}&end_date={str(end_date)}&base={base_currency_graph}&symbols={req_currency_graph}"
    response = requests.get(url_history)
    return response.json()["rates"]


def get_graph_for_7_day(json_timeframe_currency):
    font = {'size': 7}
    matplotlib.rc('font', **font)

    date_list = list()
    point_list = list()

    for key, value in json_timeframe_currency.items():
        date_list.append(key)
        for j, i in value.items():
            point_list.append(i)

    file_name = str(datetime.timestamp(datetime.now())).replace(".", "")
    plt.plot(date_list, point_list)
    plt.savefig(f'graphs_img/{file_name}.png', dpi=100)
    plt.clf()
    return file_name


def delete_graph_img_from_local_store(file_name):
    if os.path.exists(f'{config.base_dir}/graphs_img/{file_name}.png'):
        os.remove(f'{config.base_dir}/graphs_img/{file_name}.png')


with open('response_from_api_all_rates.json', 'r') as json_rates:
    dict_currencies_from_json = json.load(json_rates)['rates']
    list_currencies_from_response_json = list()

    for k, v in dict_currencies_from_json.items():
        list_currencies_from_response_json.append(f'{k}: {round(v, 2)}')
