import requests
from .models import Currency, Bank, CurrencyExchangeRate
import logging

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

def fetch_currency_data_azizimoliya():
    url = "https://azizimoliya.tj/rates-api/"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()  # Это словарь, не список

    result = []
    for currency_code in ["usd", "eur", "rub"]:
        item = data.get(currency_code)
        if item:
            result.append({
                "currency": currency_code.upper(),
                "buy": item.get("kassa_buy"),
                "sell": item.get("kassa_sell")
            })

    return result
def fetch_and_save_currency_data_azizimoliya():

    logger.info("Начинаю парсить Azizimoliya")
    data = fetch_currency_data_azizimoliya()
    logger.info(f"Получено данных от Azizimoliya: {data}")

    if data:
        for rate in data:
            code = rate['currency'].upper().strip()
            buy = rate['buy']
            sell = rate['sell']

            print(f"[DEBUG] {code} -> Покупка: {buy}, Продажа: {sell}")

            # Сохраняем в базу
            save_currency_data(code, buy, sell, 'Azizimoliya')

        print("[✓] Данные сохранены для Azizimoliya.")
    else:
        print("[!] Нет данных от Azizimoliya.")

    logger.info("Парсинг и сохранение Azizimoliya завершены успешно")
    return data

# Вызов
#rates = fetch_currency_data_azizimoliya()
#for rate in rates:
#    print(rate)
