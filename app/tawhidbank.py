import logging
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
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
    options.add_argument("--disable-javascript")
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
        # WebDriverManager сам определит подходящую версию
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

        buy = float(buy_rate)
        sell = float(sell_rate)

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


def fetch_currency_data_tawhidbank():
    """
    Парсит валютные курсы с сайта Tawhidbank
    """
    driver = None
    try:
        driver = get_chrome_driver()

        # Устанавливаем таймауты
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)

        logger.info("Загружаю страницу Tawhidbank...")
        driver.get("https://www.tawhidbank.tj/personal")

        # Ждем загрузки элементов с курсами
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rate-row"))
        )

        html = driver.page_source
        logger.info("Страница успешно загружена")

    except Exception as e:
        logger.error(f"[!] Ошибка при загрузке страницы: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Предупреждение при закрытии драйвера: {e}")

    if not html:
        logger.warning("[!] HTML пустой — возможно, сайт не загрузился.")
        return []

    # Парсим HTML
    soup = BeautifulSoup(html, 'lxml')
    rate_rows = soup.find_all("div", class_="rate-row")
    logger.info(f"Найдено блоков с курсами: {len(rate_rows)}")

    result = []

    for row in rate_rows:
        try:
            currency_tag = row.find("div", class_="currency-name")
            rates = row.find_all("div", class_="rate")

            if currency_tag and len(rates) >= 2:
                currency_name = currency_tag.text.strip().upper()
                buy_text = rates[0].text.strip().replace(',', '.')
                sell_text = rates[1].text.strip().replace(',', '.')

                # Очищаем текст от лишних символов
                buy_text = re.sub(r'[^\d.]', '', buy_text)
                sell_text = re.sub(r'[^\d.]', '', sell_text)

                if buy_text and sell_text:
                    result.append({
                        "currency": currency_name,
                        "buy": float(buy_text),
                        "sell": float(sell_text)
                    })
                    logger.debug(f"Обработан курс: {currency_name} - {buy_text}/{sell_text}")
                else:
                    logger.warning(f"Пустые курсы для {currency_name}: {buy_text}/{sell_text}")
            else:
                logger.warning("Пропущен блок: не хватает данных о валюте или курсах")

        except Exception as e:
            logger.error(f"Ошибка при обработке блока курса: {e}")
            continue

    logger.info(f"Успешно обработано {len(result)} валютных курсов")
    return result


def fetch_and_save_currency_data_tawhidbank():
    """
    Основная функция для парсинга и сохранения данных Tawhidbank
    """
    logger.info("Начинаю парсинг Tawhidbank")

    try:
        data = fetch_currency_data_tawhidbank()

        if data:
            successful_saves = 0
            for rate in data:
                try:
                    save_currency_data(
                        currency_code=rate["currency"],
                        buy_rate=rate["buy"],
                        sell_rate=rate["sell"],
                        bank_name="Tawhidbank"
                    )
                    successful_saves += 1
                except Exception as e:
                    logger.error(f"Ошибка при сохранении курса {rate['currency']}: {e}")

            logger.info(f"[✓] Успешно сохранено {successful_saves} из {len(data)} курсов для Tawhidbank")
        else:
            logger.warning("[!] Нет данных от Tawhidbank")

        logger.info("Парсинг и сохранение Tawhidbank завершены")
        return data

    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге Tawhidbank: {e}")
        return []