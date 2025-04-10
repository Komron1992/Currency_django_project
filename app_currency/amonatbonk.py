import requests


def fetch_currency_data_amonatbonk():
    # Define URL inside function
    url = 'https://amonatbonk.tj/bitrix/templates/amonatbonk/ajax/ambApi.php?_=1741425512555'

    # Sending a GET request
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        data = response.json()  # Convert the response to JSON format
        individuals = data.get('individuals', {})  # Extracting data from 'individuals'
        return individuals  # We are bringing back the dictionary with courses for individuals
    else:
        print(f"Error while requesting: {response.status_code}")
        return {}  # Return an empty dictionary in case of error


# Example of use
exchange_rates = fetch_currency_data_amonatbonk()

# We output the result
print(exchange_rates)
