import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
from .models import Currency, Bank, CurrencyExchangeRate
import logging

logger = logging.getLogger(__name__)

# Disabling SSL warnings
warnings.simplefilter('ignore', InsecureRequestWarning)

def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    # Проверяем, существует ли такая валюта в базе
    currency, created = Currency.objects.get_or_create(code=currency_code)

    # Получаем или создаём банк
    bank, created = Bank.objects.get_or_create(name=bank_name)

    # Создаём запись о курсе валюты для данного банка
    CurrencyExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )

def fetch_currency_data_arvand():
    url = 'https://arvand.tj/api/currencies/'
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        data = response.json()
        currencies = {}

        for currency_info in data:
            currency_name = currency_info['currency_name']
            buy_rate = currency_info['buy_rate']
            sell_rate = currency_info['sell_rate']
            type_currency = currency_info['type_currency']

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

        return currencies
    else:
        return None


def fetch_and_save_currency_data_arvand():
    # Получаем данные из Arvand
    logger.info("Начинаю парсить Arvand")
    data = fetch_currency_data_arvand()
    logger.info(f"Получено данных от Arvand: {data}")

    if data:
        # Пример: сохраняем курсы для валют USD, EUR, RUR
        if 'USD' in data:
            usd_data = data['USD']
            print(f"[DEBUG] USD -> Покупка: {usd_data['buy_rate']}, Продажа: {usd_data['sell_rate']}")
            save_currency_data('USD', usd_data['buy_rate'], usd_data['sell_rate'], 'Arvand')

        if 'EUR' in data:
            eur_data = data['EUR']
            print(f"[DEBUG] EUR -> Покупка: {eur_data['buy_rate']}, Продажа: {eur_data['sell_rate']}")
            save_currency_data('EUR', eur_data['buy_rate'], eur_data['sell_rate'], 'Arvand')

        if 'RUB' in data:
            rub_data = data['RUB']
            print(f"[DEBUG] RUB -> Покупка: {rub_data['buy_rate']}, Продажа: {rub_data['sell_rate']}")
            save_currency_data('RUB', rub_data['buy_rate'], rub_data['sell_rate'], 'Arvand')

        print("[✓] Данные сохранены для Arvand.")
    else:
        print("[!] Нет данных от Arvand.")

    logger.info("Парсинг и сохранение Arvand завершены успешно")
    return data

# Вызов функции
#if __name__ == '__main__':
#    data = fetch_currency_data_arvand()
#    print(data)  # Показываем результат в консоли

#    fetch_and_save_currency_data_arvand()  # Сохраняем в БД
