from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Настройки Chrome
def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск в безголовом режиме (без графического интерфейса)
    chrome_options.add_argument("--disable-gpu")  # Для Windows, чтобы избежать проблем с GPU
    chrome_options.add_argument("--no-sandbox")  # Для некоторых систем (например, на сервере)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")

    # Отключаем загрузку изображений (экономия трафика)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options

# Функция для создания и настройки драйвера
def create_driver():
    chrome_options = setup_chrome_options()

    # Указываем путь к ChromeDriver
    try:
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        print(f"Ошибка при установке ChromeDriver: {e}")
        exit(1)

    # Инициализация драйвера
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(120)  # Увеличиваем время ожидания для загрузки страницы

    return driver

# Функция для получения данных о валюте (без атрибута driver)
def fetch_currency_data_imon():
    try:
        # Создаем драйвер внутри функции
        driver = create_driver()

        # URL и время ожидания задаются внутри функции
        url = 'https://www.imon.tj/'
        wait_time = 120

        # Переходим на страницу
        driver.get(url)

        # Увеличиваем время ожидания для нахождения элементов
        try:
            currencies = WebDriverWait(driver, wait_time).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.currancy'))
            )

            # Ищем элементы, относящиеся к валютам
            currency_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.col-12.col-md')

            # Для каждой валюты ищем значения "Харид" и "Фуруш"
            currency_data = {}

            for block in currency_blocks:
                try:
                    # Для Доллара
                    if 'dollar.svg' in block.get_attribute('innerHTML'):
                        currency_name = "Доллар"
                        try:
                            buy_value = block.find_element(By.XPATH,
                                                           ".//p[contains(text(), 'Харид')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                            sell_value = block.find_element(By.XPATH,
                                                            ".//p[contains(text(), 'Фуруш')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                        except NoSuchElementException:
                            continue

                    # Для Евро
                    elif 'euro.svg' in block.get_attribute('innerHTML'):
                        currency_name = "Евро"
                        try:
                            buy_value = block.find_element(By.XPATH,
                                                           ".//p[contains(text(), 'Харид')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                            sell_value = block.find_element(By.XPATH,
                                                            ".//p[contains(text(), 'Фуруш')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                        except NoSuchElementException:
                            continue

                    # Для Рубля
                    elif 'rub.svg' in block.get_attribute('innerHTML'):
                        currency_name = "Рубль"
                        try:
                            buy_value = block.find_element(By.XPATH,
                                                           ".//p[contains(text(), 'Харид')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                            sell_value = block.find_element(By.XPATH,
                                                            ".//p[contains(text(), 'Фуруш')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                        except NoSuchElementException:
                            continue

                    else:
                        continue

                    # Добавляем данные о валюте в словарь
                    currency_data[currency_name] = {
                        'buy': buy_value,
                        'sell': sell_value
                    }

                except NoSuchElementException as e:
                    print(f"Не удалось найти данные для валюты: {e}")

            # Возвращаем словарь с данными о валютах
            if currency_data:
                return currency_data
            else:
                print("Не удалось найти данные для валют.")
                return {}

        except TimeoutException:
            print("Элементы с валютами не найдены на странице.")
            return {}

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return {}

    finally:
        # Закрываем браузер
        driver.quit()


# Пример использования:
currency_data = fetch_currency_data_imon()

# Выводим результат в формате словаря
print(currency_data)
