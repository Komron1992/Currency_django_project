# app_currency/arvand.py
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Disabling SSL warnings
warnings.simplefilter('ignore', InsecureRequestWarning)


def fetch_currency_data_arvand():
    url = 'https://arvand.tj/api/currencies/'

    # Sending a GET request with SSL certificate verification disabled
    print(f"Отправка запроса к {url}...")  # Add output to see the request
    response = requests.get(url, verify=False)

    # We check that the request was successful
    if response.status_code == 200:
        print(f"Received a successful response with code {response.status_code}")  # Logging a successful response
        # Convert the response to JSON
        data = response.json()
        print(f"Response from the server: {data}")  # Logging the server response

        currencies = {}

        # We print exchange rates
        for currency_info in data:
            currency_name = currency_info['currency_name']
            buy_rate = currency_info['buy_rate']
            sell_rate = currency_info['sell_rate']
            type_currency = currency_info['type_currency']

            # If the rate is for the CASH_RATE type, we save it
            if type_currency == 'CASH_RATE':
                if currency_name not in currencies:
                    currencies[currency_name] = {
                        'buy_rate': buy_rate,
                        'sell_rate': sell_rate
                    }

        if currencies:
            print(f"Find currency: {currencies}")  # We log that currencies were found
        else:
            print("No currencies with type CASH_RATE found.")  # If there are no currencies with the CASH_RATE type

        # We return the received data
        return currencies

    else:
        print(f"Error while requesting data, status code: {response.status_code}")
        return None
data = fetch_currency_data_arvand()
print(data)