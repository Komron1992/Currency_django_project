from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from .models import Currency, Bank, ExchangeRate

# Setting Chrome
def setup_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")  # For Windows to avoid GPU issues
    chrome_options.add_argument("--no-sandbox")  # For some systems (eg on a server)
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")

    # Disable image loading (saving traffic)
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)

    return chrome_options

# Function for creating and configuring a driver
def create_driver():
    chrome_options = setup_chrome_options()

    # Specify the path to ChromeDriver
    try:
        service = Service(ChromeDriverManager().install())
    except Exception as e:
        print(f"Error installing ChromeDriver: {e}")
        exit(1)

    # Initializing the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(120)  # Increase the waiting time for page loading

    return driver

# Function to save currency data to database
def save_currency_data(currency_code, buy_rate, sell_rate, bank_name):
    # Check if the currency exists in the database
    currency, created = Currency.objects.get_or_create(code=currency_code)

    # Get or create the bank
    bank, created = Bank.objects.get_or_create(name=bank_name)

    # Create a record of the exchange rate for the bank
    ExchangeRate.objects.create(
        bank=bank,
        currency=currency,
        buy=buy_rate,
        sell=sell_rate
    )

def fetch_currency_data_imon():
    try:
        # Create a driver inside the function
        driver = create_driver()

        # The URL and timeout are set inside the function
        url = 'https://www.imon.tj/'
        wait_time = 120

        # Let's go to the page
        driver.get(url)

        # Increase the wait time for finding elements
        try:
            currencies = WebDriverWait(driver, wait_time).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.currancy'))
            )

            # We are looking for elements related to currencies
            currency_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.col-12.col-md')

            # For each currency we look for the values of "Harid" and "Furush"
            currency_data = {}

            for block in currency_blocks:
                try:
                    # For Dollar
                    if 'dollar.svg' in block.get_attribute('innerHTML'):
                        currency_name = "Dollar"
                        try:
                            buy_value = block.find_element(By.XPATH,
                                                           ".//p[contains(text(), 'Харид')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                            sell_value = block.find_element(By.XPATH,
                                                            ".//p[contains(text(), 'Фуруш')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                        except NoSuchElementException:
                            continue

                    # For Euro
                    elif 'euro.svg' in block.get_attribute('innerHTML'):
                        currency_name = "EURO"
                        try:
                            buy_value = block.find_element(By.XPATH,
                                                           ".//p[contains(text(), 'Харид')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                            sell_value = block.find_element(By.XPATH,
                                                            ".//p[contains(text(), 'Фуруш')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                        except NoSuchElementException:
                            continue

                    # For the Ruble
                    elif 'rub.svg' in block.get_attribute('innerHTML'):
                        currency_name = "Ruble"
                        try:
                            buy_value = block.find_element(By.XPATH,
                                                           ".//p[contains(text(), 'Харид')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                            sell_value = block.find_element(By.XPATH,
                                                            ".//p[contains(text(), 'Фуруш')]/following-sibling::div//span[contains(@class, 'buy-dollar')]").text.strip()
                        except NoSuchElementException:
                            continue

                    else:
                        continue

                    # Adding currency data to the dictionary
                    currency_data[currency_name] = {
                        'buy': buy_value,
                        'sell': sell_value
                    }

                except NoSuchElementException as e:
                    print(f"Unable to find data for currency: {e}")

            # Return a dictionary with currency data
            if currency_data:
                return currency_data
            else:
                print("Unable to find data for currencies.")
                return {}

        except TimeoutException:
            print("No currency items found on page.")
            return {}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}

    finally:
        # Close browser
        driver.quit()

def fetch_and_save_currency_data_imon():
    # Fetch the currency data from Imon
    data = fetch_currency_data_imon()

    if data:
        # Save USD data
        if 'Dollar' in data:
            dollar_data = data['Dollar']
            save_currency_data('USD', dollar_data['buy'], dollar_data['sell'], 'Imon')

        # Save EURO data
        if 'EURO' in data:
            euro_data = data['EURO']
            save_currency_data('EUR', euro_data['buy'], euro_data['sell'], 'Imon')

        # Save RUR data
        if 'Ruble' in data:
            ruble_data = data['Ruble']
            save_currency_data('RUR', ruble_data['buy'], ruble_data['sell'], 'Imon')

        print("[✓] Data saved for Imon.")
    else:
        print("[!] No data from Imon.")

# Example of use:
fetch_and_save_currency_data_imon()
