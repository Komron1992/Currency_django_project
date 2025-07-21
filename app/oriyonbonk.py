import requests
import logging
from bs4 import BeautifulSoup as BS
from .models import Currency, Bank, CurrencyExchangeRate  # Абсолютный импорт

logger = logging.getLogger(__name__)

def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    print(f"save_currency_data called with currency_code={currency_code}")
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
    CurrencyExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )
    print(f"Exchange rate for {currency_code} saved.")

def fetch_currency_data_oriyonbonk():
    url = 'https://oriyonbonk.tj/ru'
    response = requests.get(url)
    soup = BS(response.text, 'lxml')

    currency_blocks = soup.find_all('div', class_='grid grid-cols-[2fr_1fr_1fr] gap-x-10 py-4 border-b-border border-solid border-b')
    currency_data = {}

    for block in currency_blocks:
        currency_name = block.find('p').text.strip()
        currency_name = currency_name.split(" ", 1)[1]  # "1 USD" -> "USD"

        p_elements = block.find_all('p', class_='text-right')
        if len(p_elements) >= 2:
            buy_price = p_elements[0].text.strip()
            sell_price = p_elements[1].text.strip()

            currency_data[currency_name] = {
                'buy': buy_price,
                'sell': sell_price
            }
    return currency_data



def fetch_and_save_currency_data_oriyonbonk():
    logger.info("Начинаю парсить Oriyonbonk")
    data = fetch_currency_data_oriyonbonk()
    logger.info(f"Получено данных от Oriyonbonk: {data}")
    if not data:
        print("[!] Нет данных от Oriyonbonk.")
        return

    for code in data:
        print(f"Saving currency: {code}")
        save_currency_data(code, data[code]['buy'], data[code]['sell'], 'Oriyonbonk')

    logger.info("Парсинг и сохранение Oriyonbonk завершены успешно")
    return data  # ✅ добавь это



#if __name__ == '__main__':
#    data = fetch_currency_data_oriyonbonk()
#    print(data)  # Показываем результат в консоли

#    fetch_and_save_currency_data_oriyonbonk()  # Сохраняем в БД
