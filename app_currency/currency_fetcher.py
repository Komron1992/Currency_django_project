from .eskhata import fetch_currency_data
from .arvand import fetch_currency_data_arvand
from .imon import fetch_currency_data_imon
from .orionbonk import fetch_currency_data_orionbonk
from .amonatbonk import fetch_currency_data_amonatbonk

def fetch_all_currency_data():
    # Получаем данные из всех источников
    data_eskhata = fetch_currency_data()
    print("Data from Eskhata:", data_eskhata)
    data_arvand = fetch_currency_data_arvand()
    print("Data from Arvand:", data_arvand)
    data_imon = fetch_currency_data_imon()
    print("Data from Imon:", data_imon)
    data_orionbonk = fetch_currency_data_orionbonk()
    print("Data from Orionbonk:", data_orionbonk)
    data_amonatbonk = fetch_currency_data_amonatbonk()
    print("Data from Amonatbonk:", data_amonatbonk)

    # Если данные получены, объединяем их
    combined_data = {}

    # Объединяем данные от eskhata, если они есть
    if data_eskhata:
        for key, value in data_eskhata.items():
            combined_data[key] = {"data": value, "source": "Eskhata"}
    else:
        print("Нет данных от Eskhata.")

    # Объединяем данные от arvand, если они есть
    if data_arvand:
        for key, value in data_arvand.items():
            if key not in combined_data:
                combined_data[key] = {"data": value, "source": "Arvand"}
    else:
        print("Нет данных от Arvand.")

    # Объединяем данные от imon, если они есть
    if data_imon:
        for key, value in data_imon.items():
            combined_data[key] = {"data": value, "source": "Imon"}
    else:
        print("Нет данных от Imon.")

    # Объединяем данные от orionbonk, если они есть
    if data_orionbonk:
        for key, value in data_orionbonk.items():
            if key not in combined_data:
                combined_data[key] = {"data": value, "source": "Orionbonk"}
    else:
        print("Нет данных от Orionbonk.")

    # Объединяем данные от amonatbonk, если они есть
    if data_amonatbonk:
        for key, value in data_amonatbonk.items():
            if key not in combined_data:
                combined_data[key] = {"data": value, "source": "Amonatbonk"}
    else:
        print("Нет данных от Amonatbonk.")

    # Возвращаем объединённые данные
    if combined_data:
        print("Combined Data:", combined_data)
        return combined_data
    else:
        print("Не удалось получить данные с одного или обоих источников.")
        return None

# Вызов функции
x = fetch_all_currency_data()
print("Final combined data:", x)
