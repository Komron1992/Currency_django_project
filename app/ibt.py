import requests
import logging
from bs4 import BeautifulSoup
import random
import urllib3
from .models import Currency, Bank, CurrencyExchangeRate

# Отключаем предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


def get_random_user_agent():
    """
    Возвращает случайный User-Agent
    """
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    return random.choice(user_agents)


def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    """
    Сохраняет данные о курсе валют в базу данных
    """
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


def extract_rates_from_table(table):
    """
    Извлекает курсы валют из таблицы (специально для IBT.tj)
    """
    rates_data = []

    try:
        # Находим tbody или работаем с основной таблицей
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
        else:
            rows = table.find_all('tr')

        for row in rows:
            # Ищем строки с курсами (пропускаем заголовки)
            th_cell = row.find('th')
            td_cells = row.find_all('td')

            if th_cell and len(td_cells) >= 2:
                # Извлекаем валюту из th
                currency_text = th_cell.get_text(strip=True).upper()

                # Проверяем, что это валютный код
                if currency_text in ['USD', 'EUR', 'RUB']:
                    try:
                        # Извлекаем курс покупки (первая td)
                        buy_rate = td_cells[0].get_text(strip=True)

                        # Извлекаем курс продажи (вторая td)
                        sell_rate = td_cells[1].get_text(strip=True)

                        rates_data.append({
                            'currency': currency_text,
                            'buy': buy_rate,
                            'sell': sell_rate
                        })

                    except (ValueError, IndexError) as e:
                        logger.error(f"Ошибка при обработке курса {currency_text}: {e}")

    except Exception as e:
        logger.error(f"Ошибка при извлечении данных из таблицы: {e}")

    return rates_data


def fetch_currency_data_ibt():
    """
    Получает данные о курсах валют с сайта IBT.tj (только из div#ibt)
    """
    url = 'https://www.ibt.tj/'

    try:
        # Настройка сессии
        session = requests.Session()
        session.verify = False

        headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        # Отправляем запрос
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Получаем HTML и создаем объект BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем конкретный div с id="ibt"
        ibt_div = soup.find('div', {'id': 'ibt'})

        if not ibt_div:
            logger.warning("Не найден div с id='ibt'")
            return []

        # Ищем таблицу внутри этого div
        table = ibt_div.find('table', class_='table mb-0')

        if not table:
            # Пробуем найти любую таблицу в этом div
            table = ibt_div.find('table')

        if table:
            # Проверяем, содержит ли таблица валютные данные
            table_text = table.get_text().upper()
            if any(currency in table_text for currency in ['USD', 'EUR', 'RUB']):
                rates = extract_rates_from_table(table)
                return rates
            else:
                logger.warning("Таблица не содержит валютные данные")
        else:
            logger.warning("Таблица не найдена в разделе МБТ(Наличные)")

        return []

    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к {url}: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при парсинге {url}: {e}")
        return []


def fetch_and_save_currency_data_ibt():
    """
    Получает и сохраняет данные о курсах валют с сайта IBT.tj
    """
    logger.info("Начинаю парсить IBT")
    data = fetch_currency_data_ibt()
    logger.info(f"Получено данных от IBT: {data}")

    if data:
        for rate in data:
            code = rate['currency'].upper().strip()
            buy = rate['buy']
            sell = rate['sell']

            print(f"[DEBUG] {code} -> Покупка: {buy}, Продажа: {sell}")

            # Сохраняем в базу
            save_currency_data(code, buy, sell, 'IBT')

        print("[✓] Данные сохранены для IBT.")
    else:
        print("[!] Нет данных от IBT.")

    logger.info("Парсинг и сохранение IBT завершены успешно")
    return data