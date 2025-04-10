import requests
from bs4 import BeautifulSoup as BS

def fetch_currency_data_orionbonk():
    # Fixed Page URL
    url = 'https://oriyonbonk.tj/ru'

    # We get the page
    response = requests.get(url)
    soup = BS(response.text, 'lxml')

    # Find all currency blocks
    currency_blocks = soup.find_all('div', class_='grid grid-cols-[2fr_1fr_1fr] gap-x-10 py-4 border-b-border border-solid border-b')

    # Dictionary for storing currency data
    currency_data = {}

    # We go through all the currency blocks
    for block in currency_blocks:
        # Extracting currency
        currency_name = block.find('p').text.strip()

        # Extracting Buy and Sell Rates
        p_elements = block.find_all('p', class_='text-right')

        # We check that both courses are present
        if len(p_elements) >= 2:
            buy_price = p_elements[0].text.strip()  # The first <p> is the purchase rate
            sell_price = p_elements[1].text.strip()  # The second <p> is the selling rate

            # Adding data to the dictionary
            currency_data[currency_name] = {
                'buy_price': buy_price,
                'sell_price': sell_price
            }

    return currency_data

# Example of using the function
currency_rates = fetch_currency_data_orionbonk()

# We output the result
print(currency_rates)
