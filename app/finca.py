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

def fetch_currency_data_finca():
    url = "https://finca.tj/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.select_one('div.finca-table-rate table')

    result = []
    if table:
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 3:
                currency = cols[0].get_text(strip=True)
                buy = cols[1].get_text(strip=True)
                sell = cols[2].get_text(strip=True)

                if currency in ["USD", "EUR", "RUB"]:
                    result.append({
                        "currency": currency,
                        "buy": buy,
                        "sell": sell
                    })

    return result

def fetch_and_save_currency_data_finca():
    logger.info("Начинаю парсить Finca")
    data = fetch_currency_data_finca()
    logger.info(f"Получено данных от Finca: {data}")

    if data:
        for rate in data:
            code = rate['currency'].upper().strip()
            buy = rate['buy']
            sell = rate['sell']

            print(f"[DEBUG] {code} -> Покупка: {buy}, Продажа: {sell}")

            # Сохраняем в базу
            save_currency_data(code, buy, sell, 'Finca')

        print("[✓] Данные сохранены для Finca.")
    else:
        print("[!] Нет данных от Finca.")

    logger.info("Парсинг и сохранение Finca завершены успешно")
    return data
# Вызов
#rates = fetch_currency_data_finca()
#for rate in rates:
#    print(rate)
