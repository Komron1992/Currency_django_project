import logging
import re
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from .models import Currency, Bank, CurrencyExchangeRate

logger = logging.getLogger(__name__)


def get_chrome_driver():
    """
    Создает и возвращает настроенный Chrome WebDriver для BRT
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--log-level=3')
    options.add_argument('--silent')

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
        # Устанавливаем совместимый ChromeDriver
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


def fetch_currency_data_brt():
    """
    Парсит валютные курсы с сайта BRT
    """
    driver = None
    html = None

    try:
        driver = get_chrome_driver()

        # Устанавливаем таймауты
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(45)

        logger.info("Загружаю страницу BRT...")
        driver.get("https://www.brt.tj/")

        # Удаляем webdriver property для обхода детекции
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Ждем загрузки начального контента
        time.sleep(3)

        logger.info("Ожидание загрузки таблицы курсов...")
        wait = WebDriverWait(driver, 45)

        # Расширенный список селекторов для поиска таблицы
        table_selectors = [
            "table[aria-live='polite']",
            "table.table",
            ".currency-table",
            "[data-testid='exchange-table']",
            "table[class*='currency']",
            "table[class*='exchange']",
            "table[class*='rate']",
            "div[class*='currency'] table",
            "div[class*='exchange'] table",
            ".exchange-rates table",
            "table"
        ]

        table_element = None

        # Пробуем найти таблицу разными способами
        for i, selector in enumerate(table_selectors):
            try:
                logger.debug(f"Пробуем селектор {i + 1}/{len(table_selectors)}: {selector}")

                table_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )

                wait.until(EC.visibility_of(table_element))

                # Проверяем, содержит ли таблица данные о валютах
                table_text = table_element.text.upper()

                if any(currency in table_text for currency in ['USD', 'EUR', 'RUB', 'ДОЛЛАР', 'ЕВРО']):
                    logger.info(f"Таблица найдена селектором: {selector}")
                    break
                else:
                    logger.debug(f"Элемент найден, но не содержит валютные данные")
                    table_element = None

            except TimeoutException:
                logger.debug(f"Таймаут для селектора: {selector}")
                continue
            except Exception as e:
                logger.debug(f"Ошибка для селектора {selector}: {e}")
                continue

        # Если таблица не найдена стандартными способами
        if not table_element:
            logger.info("Ищем альтернативными методами...")
            time.sleep(10)

            # Попытка найти элементы с валютными данными
            currency_patterns = [
                "//*[contains(text(), 'USD')]",
                "//*[contains(text(), 'EUR')]",
                "//*[contains(text(), 'RUB')]",
                "//*[contains(text(), 'доллар')]",
                "//*[contains(text(), 'евро')]"
            ]

            currency_elements = []
            for pattern in currency_patterns:
                try:
                    elements = driver.find_elements(By.XPATH, pattern)
                    currency_elements.extend(elements)
                except:
                    continue

            if currency_elements:
                logger.info(f"Найдены элементы с валютами: {len(currency_elements)}")

                # Пытаемся найти родительскую таблицу
                for elem in currency_elements:
                    try:
                        parent_table = elem.find_element(By.XPATH, "./ancestor::table[1]")
                        if parent_table:
                            table_element = parent_table
                            logger.info("Найдена родительская таблица")
                            break
                    except:
                        continue

        if not table_element:
            logger.warning("Таблица курсов не найдена или не загрузилась")
            return []

        # Получаем HTML после полной загрузки
        html = driver.page_source
        logger.info("Страница успешно загружена")

    except WebDriverException as e:
        error_msg = str(e)
        if "version" in error_msg.lower() and "chrome" in error_msg.lower():
            logger.error(f"Проблема с версией ChromeDriver: {error_msg}")
        else:
            logger.error(f"Ошибка WebDriver: {error_msg}")
        return []
    except Exception as e:
        logger.error(f"Ошибка при загрузке страницы BRT: {e}")
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
    soup = BeautifulSoup(html, 'html.parser')

    # Расширенный поиск таблицы
    table_selectors = [
        'table[aria-live="polite"]',
        'table.table',
        '.currency-table',
        'table[class*="currency"]',
        'table[class*="exchange"]',
        'table[class*="rate"]'
    ]

    table = None
    for selector in table_selectors:
        table = soup.select_one(selector)
        if table:
            break

    # Альтернативный поиск
    if not table:
        tables = soup.find_all('table')
        for t in tables:
            text = t.get_text().upper()
            if any(currency in text for currency in ['USD', 'EUR', 'RUB', 'ДОЛЛАР', 'ЕВРО']):
                table = t
                break

    if not table:
        logger.warning("[!] Таблица курсов не найдена в HTML")
        return []

    logger.info("Таблица найдена, извлекаем данные...")

    result = []
    rows = table.find_all('tr')
    logger.info(f"Найдено строк с курсами: {len(rows)}")

    for row in rows:
        try:
            cells = row.find_all(['td', 'th'])

            if len(cells) >= 3:
                # Пропускаем заголовки
                cell_text = cells[0].get_text().strip()
                if any(header in cell_text.lower() for header in ['асъор', 'валюта', 'currency', 'код']):
                    continue

                # Получаем текст валюты
                currency_text = cell_text

                # Также проверяем div внутри ячейки
                currency_div = cells[0].find('div')
                if currency_div:
                    div_text = currency_div.get_text().strip()
                    if div_text:
                        currency_text = div_text

                # Расширенные паттерны для извлечения валют
                currency_patterns = [
                    r'(\d+)\s+([A-Z]{3})',  # "1 USD"
                    r'([A-Z]{3})\s+(\d+)',  # "USD 1"
                    r'([A-Z]{3})',  # Просто "USD"
                ]

                currency = None
                amount = 1

                for pattern in currency_patterns:
                    match = re.search(pattern, currency_text.upper())
                    if match:
                        if len(match.groups()) == 2:
                            if match.group(1).isdigit():
                                amount = int(match.group(1))
                                currency = match.group(2)
                            else:
                                currency = match.group(1)
                                amount = int(match.group(2))
                        else:
                            currency = match.group(1)
                            amount = 1
                        break

                if currency and currency in ['USD', 'EUR', 'RUB']:
                    # Получаем курсы покупки и продажи
                    buy_text = cells[1].get_text().strip()
                    sell_text = cells[2].get_text().strip()

                    # Очищаем от лишних символов
                    buy_text = re.sub(r'[^\d.,]', '', buy_text).replace(',', '.')
                    sell_text = re.sub(r'[^\d.,]', '', sell_text).replace(',', '.')

                    if buy_text and sell_text:
                        result.append({
                            "currency": currency,
                            "buy": float(buy_text),
                            "sell": float(sell_text)
                        })
                        logger.debug(f"Обработан курс: {currency} - {buy_text}/{sell_text}")
                    else:
                        logger.warning(f"Пустые курсы для {currency}: {buy_text}/{sell_text}")

        except Exception as e:
            logger.error(f"Ошибка при обработке строки: {e}")
            continue

    logger.info(f"Успешно обработано {len(result)} валютных курсов")
    return result


def fetch_and_save_currency_data_brt():
    """
    Основная функция для парсинга и сохранения данных BRT
    """
    logger.info("Начинаю парсинг Банка Республики Таджикистан (BRT)")

    try:
        data = fetch_currency_data_brt()

        if data:
            successful_saves = 0
            for rate in data:
                try:
                    save_currency_data(
                        currency_code=rate["currency"],
                        buy_rate=rate["buy"],
                        sell_rate=rate["sell"],
                        bank_name="Банк Республики Таджикистан"
                    )
                    successful_saves += 1
                except Exception as e:
                    logger.error(f"Ошибка при сохранении курса {rate['currency']}: {e}")

            logger.info(f"[✓] Успешно сохранено {successful_saves} из {len(data)} курсов для BRT")
        else:
            logger.warning("[!] Нет данных от BRT")

        logger.info("Парсинг и сохранение BRT завершены")
        return data

    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге BRT: {e}")
        return []