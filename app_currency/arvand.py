import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
from .models import Currency, Bank, ExchangeRate

# Disabling SSL warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    # Проверяем, существует ли такая валюта в базе
    currency, created = Currency.objects.get_or_create(code=currency_code)

    # Получаем или создаём банк
    bank, created = Bank.objects.get_or_create(name=bank_name)

    # Создаём запись о курсе валюты для данного банка
    ExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )

def fetch_currency_data_arvand():
    url = 'https://arvand.tj/api/currencies/'

    # Отправка GET запроса с отключенной проверкой SSL сертификатов
    print(f"Отправка запроса к {url}...")
    response = requests.get(url, verify=False)

    # Проверка успешности запроса
    if response.status_code == 200:
        print(f"Получен успешный ответ с кодом {response.status_code}")
        # Преобразуем ответ в JSON
        data = response.json()
        print(f"Ответ от сервера: {data}")

        currencies = {}

        # Обрабатываем и фильтруем курсы валют по типу CASH_RATE
        for currency_info in data:
            currency_name = currency_info['currency_name']
            buy_rate = currency_info['buy_rate']
            sell_rate = currency_info['sell_rate']
            type_currency = currency_info['type_currency']

            # Если курс валюты относится к типу CASH_RATE, сохраняем его
            if type_currency == 'CASH_RATE':
                if currency_name not in currencies:
                    currencies[currency_name] = {
                        'buy_rate': buy_rate,
                        'sell_rate': sell_rate
                    }

        if currencies:
            print(f"Найденные валюты: {currencies}")
        else:
            print("Валюты с типом CASH_RATE не найдены.")

        # Возвращаем найденные валюты
        return currencies
    else:
        print(f"Ошибка при запросе данных, статус код: {response.status_code}")
        return None

def fetch_and_save_currency_data_arvand():
    # Получаем данные из Arvand
    data = fetch_currency_data_arvand()

    if data:
        # Пример: сохраняем курсы для валют USD, EUR, RUR
        if 'USD' in data:
            usd_data = data['USD']
            save_currency_data('USD', usd_data['buy_rate'], usd_data['sell_rate'], 'Arvand')

        if 'EUR' in data:
            eur_data = data['EUR']
            save_currency_data('EUR', eur_data['buy_rate'], eur_data['sell_rate'], 'Arvand')

        if 'RUR' in data:
            rur_data = data['RUR']
            save_currency_data('RUR', rur_data['buy_rate'], rur_data['sell_rate'], 'Arvand')

        print("[✓] Данные сохранены для Arvand.")
    else:
        print("[!] Нет данных от Arvand.")

# Вызов функции
fetch_and_save_currency_data_arvand()
