import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from .models import Currency, Bank, CurrencyExchangeRate

logger = logging.getLogger(__name__)


def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    currency, _ = Currency.objects.get_or_create(code=currency_code.upper())
    bank, _ = Bank.objects.get_or_create(name=bank_name)

    try:
        buy = float(str(buy_rate).replace(',', '.'))
        sell = float(str(sell_rate).replace(',', '.'))
    except ValueError:
        logger.warning(f"[!] Ошибка конвертации: {buy_rate}, {sell_rate}")
        return

    CurrencyExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy,
        sell=sell
    )
    print(f"[✓] Сохранено: {currency_code} ({bank_name}) — Покупка: {buy}, Продажа: {sell}")


def fetch_currency_data_imon():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.binary_location = "/usr/bin/chromium"

    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.set_page_load_timeout(30)
    url = "https://www.imon.tj/"
    currency_data = []
    bank_name = "Imon"

    try:
        driver.get(url)

        blocks = driver.find_elements(By.CSS_SELECTOR, "div.col-12.col-md.mt-3")

        for block in blocks:
            try:
                title = block.find_element(By.CSS_SELECTOR, "h5.title").text.strip().lower()
                if "доллар" in title:
                    code = "USD"
                elif "евро" in title:
                    code = "EUR"
                elif "рубль" in title:
                    code = "RUB"
                else:
                    continue

                row = block.find_element(By.CSS_SELECTOR, "div.row")
                cols = row.find_elements(By.CLASS_NAME, "col-6")
                if len(cols) < 2:
                    logger.warning(f"[!] Недостаточно колонок в блоке валюты {code}")
                    continue

                buy = cols[0].find_element(By.TAG_NAME, "span").text.strip()
                sell = cols[1].find_element(By.TAG_NAME, "span").text.strip()

                currency_data.append({
                    "currency": code,
                    "buy": buy,
                    "sell": sell
                })

            except NoSuchElementException:
                logger.warning(f"[!] Не удалось найти данные в блоке Imon")
            except Exception as e:
                logger.error(f"[!] Ошибка при парсинге блока Imon: {e}")

    except TimeoutException:
        logger.error("[!] Превышено время ожидания при загрузке Imon")
    except Exception as e:
        logger.error(f"[!] Ошибка при открытии Imon: {e}")
    finally:
        driver.quit()

    return currency_data


def fetch_and_save_currency_data_imon():
    logger.info("Начинаю парсить Imon")
    data = fetch_currency_data_imon()
    logger.info(f"Получено данных от Imon: {data}")

    if data:
        for item in data:
            code = item["currency"]
            buy = item["buy"]
            sell = item["sell"]

            logger.debug(f"{code} -> Покупка: {buy}, Продажа: {sell}")
            save_currency_data(code, buy, sell, "Imon")

        print("[✓] Данные сохранены для Imon.")
    else:
        print("[!] Нет данных от Imon.")

    logger.info("Парсинг и сохранение Imon завершены успешно")
    return data
