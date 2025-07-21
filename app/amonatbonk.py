import requests
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


def fetch_currency_data_amonatbonk():
    # URL для API АмонатБанк
    url = 'https://amonatbonk.tj/bitrix/templates/amonatbonk/ajax/ambApi.php?_=1741425512555'

    # Отправляем GET запрос
    response = requests.get(url)

    # Проверка успешности запроса
    if response.status_code == 200:
        data = response.json()  # Преобразуем ответ в JSON
        individuals = data.get('individuals', {})  # Извлекаем данные для частных лиц
        return individuals  # Возвращаем данные
    else:
        print(f"Ошибка при запросе: {response.status_code}")
        return {}  # Возвращаем пустой словарь в случае ошибки


def fetch_and_save_currency_data_amonatbonk():
    # Получаем данные из АмонатБанк
    logger.info("Начинаю парсить Amonatbonk")
    data = fetch_currency_data_amonatbonk()
    logger.info(f"Получено данных от Amonatbonk: {data}")

    if data:
        # Пример: получаем курсы для USD, EUR и RUR
        if 'USD' in data:
            usd_data = data['USD']
            print(f"[DEBUG] USD -> Покупка: {usd_data['buy']}, Продажа: {usd_data['sell']}")
            save_currency_data('USD', usd_data['buy'], usd_data['sell'], 'Amonatbonk')

        if 'EUR' in data:
            eur_data = data['EUR']
            print(f"[DEBUG] EUR -> Покупка: {eur_data['buy']}, Продажа: {eur_data['sell']}")
            save_currency_data('EUR', eur_data['buy'], eur_data['sell'], 'Amonatbonk')

        if 'RUB' in data:
            rub_data = data['RUB']
            print(f"[DEBUG] RUB -> Покупка: {rub_data['buy']}, Продажа: {rub_data['sell']}")
            save_currency_data('RUB', rub_data['buy'], rub_data['sell'], 'Amonatbonk')

        print("[✓] Данные сохранены для Amonatbonk.")
    else:
        print("[!] Нет данных от Amonatbonk.")

    logger.info("Парсинг и сохранение Amonatbonk завершены успешно")
    return data

#if __name__ == '__main__':
#    data = fetch_currency_data_amonatbonk()
#    print(data)  # Показываем результат в консоли
#   fetch_and_save_currency_data_amonatbonk()  # Сохраняем в БД