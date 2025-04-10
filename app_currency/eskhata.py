import requests
import fake_useragent
from bs4 import BeautifulSoup as BS

def fetch_currency_data():
    user = fake_useragent.UserAgent().random
    header = {'user-agent': user}

    url = 'https://eskhata.com/'
    r = requests.get(url, headers=header)
    soup = BS(r.text, 'lxml')

    items_word = soup.find_all('th')
    items = soup.find_all('td')

    result = {
        'usd': {
            'currency': items[0].text.strip(),
            'buy': items[1].text.strip(),
            'sell': items[2].text.strip(),
            'nbt': items[3].text.strip(),
        },
        'eur': {
            'currency': items[4].text.strip(),
            'buy': items[5].text.strip(),
            'sell': items[6].text.strip(),
            'nbt': items[7].text.strip(),
        },
        'rur': {
            'currency': items[8].text.strip(),
            'buy': items[9].text.strip(),
            'sell': items[10].text.strip(),
            'nbt': items[11].text.strip(),
        }
    }

    return result

if __name__ == '__main__':
    data = fetch_currency_data()
    print(data)
