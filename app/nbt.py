import requests
import logging
from bs4 import BeautifulSoup
from .models import Currency, Bank, CurrencyExchangeRate

logger = logging.getLogger(__name__)

URL = "https://nbt.tj/ru/kurs/kurs.php"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

TARGET_CURRENCIES = ["Доллар США", "ЕВРО", "Российский рубль"]

def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    currency, _ = Currency.objects.get_or_create(code=currency_code.upper())
    bank, _ = Bank.objects.get_or_create(name=bank_name)

    try:
        if isinstance(buy_rate, str):
            buy_rate = float(buy_rate.replace(',', '.'))
        else:
            buy_rate = float(buy_rate)

        if isinstance(sell_rate, str):
            sell_rate = float(sell_rate.replace(',', '.'))
        else:
            sell_rate = float(sell_rate)
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


def fetch_currency_data_nbt():
    response = requests.get(URL, headers=HEADERS)
    response.encoding = 'utf-8'  # Учитываем кириллицу
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("tbody", class_="new__rate__nbt-table")
    result = {}

    for row in table.find_all("tr"):
        columns = row.find_all("td")
        if len(columns) < 5:
            continue

        currency_name = columns[3].get_text(strip=True)
        rate = columns[4].get_text(strip=True)

        if currency_name in TARGET_CURRENCIES:
            result[currency_name] = float(rate.replace(',', '.'))

    return result

def fetch_and_save_currency_data_nbt():
    # Fetch the currency data from NBT
    logger.info("Начинаю парсить NBT")
    data = fetch_currency_data_nbt()
    logger.info(f"Получено данных от NBT: {data}")

    if data:
        # Save USD data
        if 'Доллар США' in data:
            rate = data['Доллар США']
            save_currency_data('USD', rate, rate, 'NBT')  # и покупка, и продажа одинаковы

        # Save EURO data
        if 'ЕВРО' in data:
            rate = data['ЕВРО']
            save_currency_data('EUR', rate, rate, 'NBT')  # и покупка, и продажа одинаковы

        # Save RUR data
        if 'Российский рубль' in data:
            rate = data['Российский рубль']
            save_currency_data('RUB', rate, rate, 'NBT')  # и покупка, и продажа одинаковы

        print("[✓] Data saved for NBT.")
    else:
        print("[!] No data from NBT.")

    logger.info("Парсинг и сохранение NBT завершены успешно")
    return data  # ✅ добавь это
#if __name__ == "__main__":
#    rates = fetch_currency_data_nbt()
#    for currency, rate in rates.items():
#        print(f"{currency}: {rate}")
