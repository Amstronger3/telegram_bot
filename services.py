import os
from datetime import datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
import requests

import config


def check_valid_currency_name(name):
    if len(name) != 3:
        return "Length of name currency must be 3 symbols only!"
    elif not name.upper() in config.currency_list:
        return "Invalid name of currency! \nExample: UAH"


def get_list_available_currency():
    url = f'{config.base_url}latest'
    response = requests.get(url)

    list_currencies_from_response_json = list()

    for key, value in response.json()["rates"].items():
        list_currencies_from_response_json.append(f'{key}: {round(value, 2)}')
    return list_currencies_from_response_json


def make_request_to_convert(currency_to, amount=10, currency_from="USD"):
    url_convert = f"{config.base_url}convert?from={currency_from}&to={currency_to}&amount={str(amount)}"
    response = requests.get(url_convert)

    return round(response.json()["result"], 2)


def make_request_to_get_graph_for_7_day(base_currency_graph="USD", req_currency_graph="CAD"):
    start_date = datetime.date(datetime.now()) - timedelta(days=7)
    end_date = datetime.date(datetime.now())
    url_history = f"{config.base_url}timeseries?" \
                  f"start_date={str(start_date)}&" \
                  f"end_date={str(end_date)}&base={base_currency_graph}&symbols={req_currency_graph}"
    response = requests.get(url_history)
    return response.json()["rates"], req_currency_graph


def get_graph_for_7_day(json_timeframe_currency, req_currency_graph):
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
    if not os.path.isdir('./graphs_img'):
        os.mkdir('./graphs_img')
    plt.gca().set(ylabel=req_currency_graph)
    plt.savefig(f'./graphs_img/{file_name}.png', dpi=100)
    plt.clf()
    return file_name


def delete_graph_img_from_local_store(file_name):
    if os.path.exists(f'{config.base_dir}/graphs_img/{file_name}.png'):
        os.remove(f'{config.base_dir}/graphs_img/{file_name}.png')
