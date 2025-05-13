import fake_useragent
import requests
from bs4 import BeautifulSoup as BS
from .models import Currency, Bank, ExchangeRate


def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    # Получаем или создаём объект валюты
    currency, _ = Currency.objects.get_or_create(code=currency_code.upper())

    # Получаем или создаём объект банка
    bank, _ = Bank.objects.get_or_create(name=bank_name)

    # Создаём запись обменного курса
    ExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )


def fetch_and_save_currency_data_eskhata():
    # Генерация случайного user-agent
    user = fake_useragent.UserAgent().random
    headers = {'User-Agent': user}

    url = 'https://eskhata.com/'
    response = requests.get(url, headers=headers)
    soup = BS(response.text, 'lxml')

    # Получаем все строки таблицы, содержащие данные
    rows = soup.find_all('tr')

    # Целевые валюты
    target_currencies = ['USD', 'EUR', 'RUB', 'RUR']  # RUB и RUR бывают в разных форматах

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            currency = cells[0].text.strip().upper()
            buy = cells[1].text.strip()
            sell = cells[2].text.strip()

            if currency in target_currencies:
                # Приводим RUR к RUB
                if currency == 'RUR':
                    currency = 'RUB'
                save_currency_data(currency, buy, sell, 'Eskhata')
