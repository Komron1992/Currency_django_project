import requests
from bs4 import BeautifulSoup as BS
from .models import Currency, Bank, ExchangeRate  # Абсолютный импорт

def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    print(f"Attempting to save {currency_code} for {bank_name}. Buy: {buy_rate}, Sell: {sell_rate}")

    # Проверяем, существует ли такая валюта в базе
    currency, created = Currency.objects.get_or_create(code=currency_code)

    # Проверяем, что валюта была создана или найдена
    if created:
        print(f"Currency {currency_code} created.")
    else:
        print(f"Currency {currency_code} already exists.")

    # Получаем или создаём банк
    bank, created = Bank.objects.get_or_create(name=bank_name)

    # Проверяем, что банк был создан или найден
    if created:
        print(f"Bank {bank_name} created.")
    else:
        print(f"Bank {bank_name} already exists.")

    # Создаём запись о курсе валюты для данного банка
    ExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )
    print(f"Exchange rate for {currency_code} saved.")

def fetch_currency_data_oriyonbonk():
    # Fixed Page URL
    url = 'https://oriyonbonk.tj/ru'

    # We get the page
    response = requests.get(url)
    soup = BS(response.text, 'lxml')

    # Find all currency blocks
    currency_blocks = soup.find_all('div', class_='grid grid-cols-[2fr_1fr_1fr] gap-x-10 py-4 border-b-border border-solid border-b')

    # Dictionary for storing currency data
    currency_data = {}

    # We go through all the currency blocks
    for block in currency_blocks:
        # Extracting currency
        currency_name = block.find('p').text.strip()

        # Remove '1 ' from the start of the currency name by splitting the string
        currency_name = currency_name.split(" ", 1)[1]

        # Extracting Buy and Sell Rates
        p_elements = block.find_all('p', class_='text-right')

        # We check that both courses are present
        if len(p_elements) >= 2:
            buy_price = p_elements[0].text.strip()  # The first <p> is the purchase rate
            sell_price = p_elements[1].text.strip()  # The second <p> is the selling rate

            # Adding data to the dictionary
            currency_data[currency_name] = {
                'buy': buy_price,
                'sell': sell_price
            }

    return currency_data


def fetch_and_save_currency_data_oriyonbonk():
    # Получаем данные о курсах валют с Oriyonbonk
    data = fetch_currency_data_oriyonbonk()

    if data:
        # Сохраняем данные по USD, если они есть
        if 'USD' in data:
            usd_data = data['USD']
            save_currency_data('USD', usd_data['buy'], usd_data['sell'], 'Oriyonbonk')

        # Сохраняем данные по EUR, если они есть
        if 'EUR' in data:
            eur_data = data['EUR']
            save_currency_data('EUR', eur_data['buy'], eur_data['sell'], 'Oriyonbonk')

        # Сохраняем данные по RUR (RUB), если они есть
        if 'RUB' in data:
            rub_data = data['RUB']
            save_currency_data('RUR', rub_data['buy'], rub_data['sell'], 'Oriyonbonk')

        print("[✓] Данные сохранены для Oriyonbonk.")
    else:
        print("[!] Нет данных от Oriyonbonk.")

if __name__ == '__main__':
    fetch_and_save_currency_data_oriyonbonk()

x=fetch_currency_data_oriyonbonk()
print(x)