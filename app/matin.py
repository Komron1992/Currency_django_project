import requests
import urllib3
import logging
from .models import Currency, Bank, CurrencyExchangeRate

logger = logging.getLogger(__name__)

# Отключаем предупреждения SSL (временно)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



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

def fetch_currency_data_matin():
    url = "https://matin.tj/api/currency"
    response = requests.get(url, verify=False)
    response.raise_for_status()

    data = response.json()
    rates = []

    for item in data:
        rates.append({
            "currency": item.get("currency"),
            "buy": item.get("valuebuy"),
            "sell": item.get("valuesale")
        })

    return rates

def fetch_and_save_currency_data_matin():
    logger.info("Начинаю парсить Matin")
    data = fetch_currency_data_matin()
    logger.info(f"Получено данных от Matin: {data}")

    if data:
        for rate in data:
            code = rate['currency'].upper().strip()
            buy = rate['buy']
            sell = rate['sell']

            print(f"[DEBUG] {code} -> Покупка: {buy}, Продажа: {sell}")

            # Сохраняем в базу
            save_currency_data(code, buy, sell, 'Matin')

        print("[✓] Данные сохранены для Matin.")
    else:
        print("[!] Нет данных от Matin.")

    logger.info("Парсинг и сохранение Matin завершены успешно")
    return data
# Пример использования
#if __name__ == "__main__":
#    data = fetch_currency_data_matin()
#    for item in data:
#        print(item)
