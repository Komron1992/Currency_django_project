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

        # Очищаем и конвертируем курсы
        buy_clean = str(buy_rate).replace(',', '.').strip()
        sell_clean = str(sell_rate).replace(',', '.').strip()

        # Очищаем от лишних символов
        buy_clean = re.sub(r'[^\d.]', '', buy_clean)
        sell_clean = re.sub(r'[^\d.]', '', sell_clean)

        buy = float(buy_clean)
        sell = float(sell_clean)

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


def fetch_currency_data_ssb():
    """
    Парсит валютные курсы с сайта Sanoatsodirotbonk
    """
    driver = None
    try:
        driver = get_chrome_driver()

        # Устанавливаем таймауты
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)

        url = "https://www.ssb.tj/ru/?type=1"
        logger.info(f"Загружаю страницу SSB: {url}")
        driver.get(url)

        # Ждем загрузки блоков с данными
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "main_block"))
        )

        # Получаем блоки
        blocks = driver.find_elements(By.CLASS_NAME, "main_block")
        logger.info(f"Найдено блоков: {len(blocks)}")

        if len(blocks) < 3:
            raise Exception(f"Недостаточно блоков с данными. Найдено: {len(blocks)}, требуется: 3")

        # Извлекаем данные из блоков
        currency_elements = blocks[0].find_elements(By.TAG_NAME, "p")
        buy_elements = blocks[1].find_elements(By.TAG_NAME, "p")
        sell_elements = blocks[2].find_elements(By.TAG_NAME, "p")

        # Фильтруем только нужные валюты
        target_currencies = ["USD", "EUR", "RUB"]
        currencies = []
        buys = []
        sells = []

        for i, el in enumerate(currency_elements):
            currency_text = el.text.strip().upper()
            if currency_text in target_currencies:
                currencies.append(currency_text)

                # Получаем соответствующие курсы
                if i < len(buy_elements):
                    buy_text = buy_elements[i].text.strip().replace(',', '.')
                    buys.append(buy_text)
                else:
                    buys.append(None)

                if i < len(sell_elements):
                    sell_text = sell_elements[i].text.strip().replace(',', '.')
                    sells.append(sell_text)
                else:
                    sells.append(None)

        logger.info(f"Найдено валют: {len(currencies)}")

        result = []
        for i in range(len(currencies)):
            currency_data = {
                "currency": currencies[i],
                "buy": buys[i] if i < len(buys) else None,
                "sell": sells[i] if i < len(sells) else None
            }
            result.append(currency_data)
            logger.debug(
                f"Обработан курс: {currency_data['currency']} - {currency_data['buy']}/{currency_data['sell']}")

        logger.info(f"Успешно обработано {len(result)} валютных курсов")
        return result

    except Exception as e:
        logger.error(f"[!] Ошибка при парсинге SSB: {e}")
        return []

    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.warning(f"Предупреждение при закрытии драйвера: {e}")


def fetch_and_save_currency_data_ssb():
    """
    Основная функция для парсинга и сохранения данных SSB
    """
    logger.info("Начинаю парсинг Sanoatsodirotbonk")

    try:
        data = fetch_currency_data_ssb()

        if data:
            successful_saves = 0
            for rate in data:
                try:
                    if rate['buy'] is not None and rate['sell'] is not None:
                        save_currency_data(
                            currency_code=rate['currency'],
                            buy_rate=rate['buy'],
                            sell_rate=rate['sell'],
                            bank_name="Sanoatsodirotbonk"
                        )
                        successful_saves += 1
                    else:
                        logger.warning(f"Пропущен курс {rate['currency']}: отсутствуют данные о покупке или продаже")
                except Exception as e:
                    logger.error(f"Ошибка при сохранении курса {rate['currency']}: {e}")

            logger.info(f"[✓] Успешно сохранено {successful_saves} из {len(data)} курсов для Sanoatsodirotbonk")
        else:
            logger.warning("[!] Нет данных от SSB")

        logger.info("Парсинг и сохранение SSB завершены")
        return data

    except Exception as e:
        logger.error(f"Критическая ошибка при парсинге SSB: {e}")
        return []