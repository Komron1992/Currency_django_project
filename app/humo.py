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


def fetch_currency_data_humo():
    url = "https://humo.tj/ru/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    humo_section = soup.find('div', class_='kursHUMO')

    result = []
    if humo_section:
        # Находим все блоки с курсами валют
        kurs_bodies = humo_section.find_all('div', class_='kursBody')

        for kurs_body in kurs_bodies:
            divs = kurs_body.find_all('div')
            if len(divs) >= 3:
                # Извлекаем валюту из первого div (например, "1 USD")
                currency_text = divs[0].get_text(strip=True)
                # Извлекаем код валюты (последние 3 символа)
                currency_code = currency_text.split()[-1]

                # Извлекаем курсы покупки и продажи
                buy = divs[1].get_text(strip=True)
                sell = divs[2].get_text(strip=True)

                if currency_code in ["USD", "EUR", "RUB"]:
                    result.append({
                        "currency": currency_code,
                        "buy": buy,
                        "sell": sell
                    })

    return result


def fetch_and_save_currency_data_humo():
    logger.info("Начинаю парсить HUMO")
    data = fetch_currency_data_humo()
    logger.info(f"Получено данных от HUMO: {data}")

    if data:
        for rate in data:
            code = rate['currency'].upper().strip()
            buy = rate['buy']
            sell = rate['sell']

            print(f"[DEBUG] {code} -> Покупка: {buy}, Продажа: {sell}")

            # Сохраняем в базу
            save_currency_data(code, buy, sell, 'HUMO')

        print("[✓] Данные сохранены для HUMO.")
    else:
        print("[!] Нет данных от HUMO.")

    logger.info("Парсинг и сохранение HUMO завершены успешно")
    return data

# Вызов
# rates = fetch_currency_data_humo()
# for rate in rates:
#    print(rate)