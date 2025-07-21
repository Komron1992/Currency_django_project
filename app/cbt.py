import requests
import logging
from bs4 import BeautifulSoup
from .models import Currency, Bank, CurrencyExchangeRate

logger = logging.getLogger(__name__)


def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    currency, _ = Currency.objects.get_or_create(code=currency_code.upper())
    bank, _ = Bank.objects.get_or_create(name=bank_name)

    try:
        buy = float(buy_rate.replace(',', '.')) if isinstance(buy_rate, str) else float(buy_rate)
        sell = float(sell_rate.replace(',', '.')) if isinstance(sell_rate, str) else float(sell_rate)
    except ValueError:
        print(f"[!] Ошибка конвертации: {buy_rate}, {sell_rate}")
        return

    CurrencyExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy,
        sell=sell
    )
    print(f"[✓] Сохранено: {currency_code} ({bank_name}) — Покупка: {buy}, Продажа: {sell}")


def fetch_currency_data_cbt():
    url = "https://cbt.tj/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    cash_table = soup.find('table', id='CASH')

    result = []
    if cash_table:
        rows = cash_table.find('tbody').find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # Извлекаем символ валюты
                currency_cell = cells[0]
                currency_symbol = currency_cell.text.strip().split()[0]

                # Конвертируем символы в коды валют
                currency_mapping = {
                    '$': 'USD',
                    '€': 'EUR',
                    '₽': 'RUB'
                }

                currency_code = currency_mapping.get(currency_symbol)
                if currency_code:
                    buy = cells[1].text.strip()
                    sell = cells[2].text.strip()

                    result.append({
                        "currency": currency_code,
                        "buy": buy,
                        "sell": sell
                    })

    return result


def fetch_and_save_currency_data_cbt():
    logger.info("Начинаю парсить CBT")
    data = fetch_currency_data_cbt()
    logger.info(f"Получено данных от CBT: {data}")

    if data:
        for rate in data:
            code = rate['currency'].upper().strip()
            buy = rate['buy']
            sell = rate['sell']

            print(f"[DEBUG] {code} -> Покупка: {buy}, Продажа: {sell}")

            # Сохраняем в базу
            save_currency_data(code, buy, sell, 'CBT')

        print("[✓] Данные сохранены для CBT.")
    else:
        print("[!] Нет данных от CBT.")

    logger.info("Парсинг и сохранение CBT завершены успешно")
    return data

# Вызов
# rates = fetch_currency_data_cbt()
# for rate in rates:
#    print(rate)