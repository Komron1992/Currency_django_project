# app/eskhata.py

import os
import sys
import django

# Устанавливаем корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

# Теперь импортируем модели
import fake_useragent
import requests
from bs4 import BeautifulSoup as BS
from app.models import Currency, Bank, CurrencyExchangeRate


def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    currency, _ = Currency.objects.get_or_create(code=currency_code.upper())
    bank, _ = Bank.objects.get_or_create(name=bank_name)

    try:
        buy_rate = float(buy_rate.replace(',', '.'))
        sell_rate = float(sell_rate.replace(',', '.'))
    except ValueError:
        print(f"Ошибка конвертации курса: buy={buy_rate}, sell={sell_rate}")
        return

    CurrencyExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )
    print(f"Saved: {bank_name} {currency_code} buy={buy_rate} sell={sell_rate}")


def fetch_and_save_currency_data_eskhata():
    user = fake_useragent.UserAgent().random
    headers = {'User-Agent': user}
    url = 'https://eskhata.com/'
    response = requests.get(url, headers=headers)
    soup = BS(response.text, 'lxml')

    rows = soup.find_all('tr')
    target_currencies = ['USD', 'EUR', 'RUB']

    found = set()

    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 3:
            currency = cells[0].text.strip().upper()

            if currency == 'RUR':
                currency = 'RUB'

            if currency not in target_currencies:
                continue

            # Если эту валюту уже нашли — пропускаем, чтобы не дублировать
            if currency in found:
                continue

            buy = cells[1].text.strip()
            sell = cells[2].text.strip()

            print(f"Parsing {currency} buy={buy} sell={sell} from Eskhata")
            save_currency_data(currency, buy, sell, 'Eskhata')
            found.add(currency)

            if found == set(target_currencies):
                break  # нашли все, выходим из цикла




#if __name__ == '__main__':
#    fetch_and_save_currency_data_eskhata()