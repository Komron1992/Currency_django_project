#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from .models import Currency, Bank, CurrencyExchangeRate
import logging

logger = logging.getLogger(__name__)


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


def fetch_currency_data_tejaratbank():
    """Получение курсов валют с сайта Течарат Банка"""
    url = "https://tejaratbank.tj/"

    try:
        # Получаем страницу
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем курсы валют
        rates = {}

        # Ищем все элементы с заголовками
        headings = soup.find_all('div', class_='elementor-heading-title')

        # Извлекаем дату
        date = None
        for heading in headings:
            text = heading.get_text().strip()
            if 'курс валют на' in text:
                date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', text)
                if date_match:
                    date = date_match.group(1)

        # Извлекаем курсы
        for i, heading in enumerate(headings):
            text = heading.get_text().strip()

            if text in ['USD', 'EURO', 'RUB']:
                try:
                    # Следующие два элемента должны содержать курсы
                    buy_rate = float(headings[i + 1].get_text().strip())
                    sell_rate = float(headings[i + 2].get_text().strip())

                    rates[text] = {
                        'buy': buy_rate,
                        'sell': sell_rate
                    }
                except (IndexError, ValueError):
                    continue

        return rates

    except Exception as e:
        logger.error(f"Ошибка при получении данных от Tejaratbank: {e}")
        return {}


def fetch_and_save_currency_data_tejaratbank():
    # Получаем данные из Течарат Банка
    logger.info("Начинаю парсить Tejaratbank")
    data = fetch_currency_data_tejaratbank()
    logger.info(f"Получено данных от Tejaratbank: {data}")

    if data:
        # Пример: получаем курсы для USD, EUR и RUB
        if 'USD' in data:
            usd_data = data['USD']
            print(f"[DEBUG] USD -> Покупка: {usd_data['buy']}, Продажа: {usd_data['sell']}")
            save_currency_data('USD', usd_data['buy'], usd_data['sell'], 'Tejaratbank')

        if 'EURO' in data:
            euro_data = data['EURO']
            print(f"[DEBUG] EUR -> Покупка: {euro_data['buy']}, Продажа: {euro_data['sell']}")
            save_currency_data('EUR', euro_data['buy'], euro_data['sell'], 'Tejaratbank')

        if 'RUB' in data:
            rub_data = data['RUB']
            print(f"[DEBUG] RUB -> Покупка: {rub_data['buy']}, Продажа: {rub_data['sell']}")
            save_currency_data('RUB', rub_data['buy'], rub_data['sell'], 'Tejaratbank')

        print("[✓] Данные сохранены для Tejaratbank.")
    else:
        print("[!] Нет данных от Tejaratbank.")

    logger.info("Парсинг и сохранение Tejaratbank завершены успешно")
    return data


# Функция для форматирования (оставлена для совместимости)
def format_rates(data):
    """Форматировать курсы для вывода"""
    if not data:
        return "❌ Ошибка: Нет данных"

    result = "🏦 Течарат Банк\n"
    result += "\n💱 Курсы валют:\n"

    currency_names = {
        'USD': 'Доллар США',
        'EURO': 'Евро',
        'RUB': 'Российский рубль'
    }

    for currency, rates in data.items():
        name = currency_names.get(currency, currency)
        result += f"\n{name} ({currency}):\n"
        result += f"  💰 Покупка: {rates['buy']}\n"
        result += f"  💸 Продажа: {rates['sell']}\n"

    return result


# Быстрый запуск для тестирования
if __name__ == "__main__":
    print("🔄 Получение курсов валют...")
    data = fetch_currency_data_tejaratbank()
    print(format_rates(data))
    # fetch_and_save_currency_data_tejaratbank()  # Раскомментировать для сохранения в БД