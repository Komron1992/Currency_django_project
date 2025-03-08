# app_currency/arvand.py
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Отключаем предупреждения SSL
warnings.simplefilter('ignore', InsecureRequestWarning)


def fetch_currency_data_arvand():
    url = 'https://arvand.tj/api/currencies/'

    # Отправляем GET-запрос с отключенной проверкой SSL-сертификата
    print(f"Отправка запроса к {url}...")  # Добавляем вывод, чтобы видеть запрос
    response = requests.get(url, verify=False)

    # Проверяем, что запрос прошел успешно
    if response.status_code == 200:
        print(f"Получен успешный ответ с кодом {response.status_code}")  # Логируем успешный ответ
        # Преобразуем ответ в JSON
        data = response.json()
        print(f"Ответ от сервера: {data}")  # Логируем ответ сервера

        currencies = {}

        # Печатаем курсы валют
        for currency_info in data:
            currency_name = currency_info['currency_name']
            buy_rate = currency_info['buy_rate']
            sell_rate = currency_info['sell_rate']
            type_currency = currency_info['type_currency']

            # Если курс для типа CASH_RATE, сохраняем его
            if type_currency == 'CASH_RATE':
                if currency_name not in currencies:
                    currencies[currency_name] = {
                        'buy_rate': buy_rate,
                        'sell_rate': sell_rate
                    }

        if currencies:
            print(f"Найденные валюты: {currencies}")  # Логируем, что были найдены валюты
        else:
            print("Не найдено валют с типом CASH_RATE.")  # Если нет валют с типом CASH_RATE

        # Возвращаем полученные данные
        return currencies

    else:
        print(f"Ошибка при запросе данных, статус код: {response.status_code}")
        return None
data = fetch_currency_data_arvand()
print(data)