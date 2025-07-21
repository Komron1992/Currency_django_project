import logging
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from .models import Currency, Bank, CurrencyExchangeRate

logger = logging.getLogger(__name__)


def get_chrome_driver():
    """
    Создает и возвращает настроенный Chrome WebDriver
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36")

    # Определяем путь к Chromium
    chrome_bin = os.environ.get('CHROME_BIN', '/usr/bin/chromium')
    if os.path.exists(chrome_bin):
        options.binary_location = chrome_bin
    else:
        # Пробуем альтернативные пути
        possible_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium'
        ]

        for path in possible_paths:
            if os.path.exists(path):
                options.binary_location = path
                break
        else:
            logger.warning("Не найден исполняемый файл Chrome/Chromium")

    try:
        # Устанавливаем совместимый ChromeDriver без указания версии
        driver_path = ChromeDriverManager().install()
        logger.info(f"ChromeDriver установлен по пути: {driver_path}")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("Chrome WebDriver успешно создан")
        return driver

    except Exception as e:
        logger.error(f"Ошибка при создании Chrome WebDriver: {e}")
        # Пробуем использовать системный chromedriver если он есть
        try:
            service = Service()  # Использует системный chromedriver
            driver = webdriver.Chrome(service=service, options=options)
            logger.info("Использован системный ChromeDriver")
            return driver
        except Exception as e2:
            logger.error(f"Ошибка при использовании системного ChromeDriver: {e2}")
            raise e2


def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    """
    Сохраняет данные о валютных курсах в базу данных
    """
    try:
        currency, _ = Currency.objects.get_or_create(code=currency_code.upper())
        bank, _ = Bank.objects.get_or_create(name=bank_name)

        buy = float(str(buy_rate).replace(',', '.'))
        sell = float(str(sell_rate).replace(',', '.'))

        CurrencyExchangeRate.objects.create(
            bank=bank,
            currency=currency,
            buy=buy,
            sell=sell
        )
        logger.info(f"[✓] Сохранено: {currency_code} ({bank_name}) — Покупка: {buy}, Продажа: {sell}")
    except ValueError as e:
        logger.warning(f"[!] Ошибка конвертации курсов: {buy_rate}, {sell_rate}. Ошибка: {e}")
    except Exception as e:
        logger.error(f"[!] Ошибка при сохранении данных: {e}")


def fetch_currency_data_spitamenbank():
    """
    Парсит валютные курсы с сайта Spitamenbank
    """
    driver = None
    try:
        driver = get_chrome_driver()

        # Устанавливаем таймауты
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)

        logger.info("Загружаю страницу Spitamenbank...")
        driver.get('https://www.spitamenbank.tj/tj/personal/')

        # Ждем загрузки элементов с курсами
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "currency-list"))
        )

        html = driver.page_source
        logger.info("Страница Spitamenbank успешно загружена")

    except Exception as e:
        logger.error(f"[!] Ошибка при загрузке страницы Spitamenbank: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Предупреждение при закрытии драйвера: {e}")

    if not html:
        logger.warning("[!] HTML пустой — возможно, сайт Spitamenbank не загрузился.")
        return []

    # Парсим HTML
    soup = BeautifulSoup(html, 'html.parser')
    target_li = soup.find('li', {'c_index': '1'})
    results = []

    if target_li:
        rows = target_li.select('.currency-values')
        logger.info(f"Найдено строк с курсами: {len(rows)}")

        rows_processed = 0
        for row in rows:
            try:
                divs = row.find_all('div', {'c-val': True})
                if len(divs) >= 3:
                    currency = divs[0].text.strip().upper()
                    buy = divs[1].get('c-val')
                    sell = divs[2].get('c-val')

                    if currency and buy and sell:
                        # Очищаем и конвертируем данные
                        buy_clean = re.sub(r'[^\d.]', '', str(buy).replace(',', '.'))
                        sell_clean = re.sub(r'[^\d.]', '', str(sell).replace(',', '.'))

                        if buy_clean and sell_clean:
                            results.append({
                                'currency': currency,
                                'buy': float(buy_clean),
                                'sell': float(sell_clean)
                            })
                            logger.debug(f"Обработан курс: {currency} - {buy_clean}/{sell_clean}")
                            rows_processed += 1
                        else:
                            logger.warning(f"Пустые очищенные курсы для {currency}: {buy_clean}/{sell_clean}")
                    else:
                        logger.warning(f"Отсутствуют данные: валюта={currency}, покупка={buy}, продажа={sell}")
                else:
                    logger.warning(f"Недостаточно div элементов в строке курса: {len(divs)}")
            except Exception as e:
                logger.error(f"Ошибка при обработке строки курса: {e}")
                continue

        logger.info(f"Успешно обработано {rows_processed} валютных курсов для Spitamenbank")
    else:
        logger.warning("[!] Не найден блок с валютами Spitamenbank (li с c_index='1').")

    return results


def fetch_and_save_currency_data_spitamenbank():
    """
    Основная функция для парсинга и сохранения данных Spitamenbank
    """
    logger.info("Начинаю парсинг Spitamenbank")

    try:
        data = fetch_currency_data_spitamenbank()

        if data:
            successful_saves = 0
            for rate in data:
                try:
                    save_currency_data(
                        currency_code=rate['currency'],
                        buy_rate=rate['buy'],
                        sell_rate=rate['sell'],
                        bank_name='Spitamenbank'
                    )
                    successful_saves += 1
                except Exception as e:
                    logger.error(f"Ошибка при сохранении курса {rate['currency']}: {e}")

            logger.info(f"[✓] Успешно сохранено {successful_saves} из {len(data)} курсов для Spitamenbank")
        else:
            logger.warning("[!] Нет данных от Spitamenbank")

        logger.info("Парсинг и сохранение Spitamenbank завершены")
        return data

    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге Spitamenbank: {e}")
        return []