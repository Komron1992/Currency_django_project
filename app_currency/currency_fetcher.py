# app_currency/currency_fetcher.py

from eskhata import fetch_currency_data
from arvand import fetch_currency_data_arvand
from imon import fetch_currency_data_imon
from orionbonk import fetch_currency_data_orionbonk

def fetch_all_currency_data():
    # Получаем данные из обоих источников
    data_eskhata = fetch_currency_data()
    data_arvand = fetch_currency_data_arvand()
    data_imon = fetch_currency_data_imon()
    data_orionbonk = fetch_currency_data_orionbonk()

    # Если данные получены, объединяем их
    if data_eskhata and data_arvand and data_imon and data_orionbonk :
        combined_data = {}

        # Объединяем данные от eskhata
        for key, value in data_eskhata.items():
            combined_data[key] = value

        # Объединяем данные от arvand
        for key, value in data_arvand.items():
            if key not in combined_data:  # Если валюта еще не добавлена, добавляем ее
                combined_data[key] = value

        # Объединяем данные от imon
        for key, value in data_imon.items():
            combined_data[key] = value

        # Объединяем данные от orionbonk
        for key, value in data_orionbonk.items():
            if key not in combined_data:  # Если валюта еще не добавлена, добавляем ее
                combined_data[key] = value

        return combined_data

    else:
        print("Не удалось получить данные с одного или обоих источников.")
        return None

data=fetch_all_currency_data()
print(data)