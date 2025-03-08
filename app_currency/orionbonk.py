import requests
from bs4 import BeautifulSoup as BS

def fetch_currency_data_orionbonk():
    # Фиксированный URL страницы
    url = 'https://oriyonbonk.tj/ru'

    # Получаем страницу
    response = requests.get(url)
    soup = BS(response.text, 'lxml')

    # Находим все блоки валют
    currency_blocks = soup.find_all('div', class_='grid grid-cols-[2fr_1fr_1fr] gap-x-10 py-4 border-b-border border-solid border-b')

    # Словарь для хранения данных о валюте
    currency_data = {}

    # Проходим по всем блокам валют
    for block in currency_blocks:
        # Извлекаем валюту
        currency_name = block.find('p').text.strip()

        # Извлекаем курсы покупки и продажи
        p_elements = block.find_all('p', class_='text-right')

        # Проверяем, что оба курса присутствуют
        if len(p_elements) >= 2:
            buy_price = p_elements[0].text.strip()  # Первый <p> - это курс покупки
            sell_price = p_elements[1].text.strip()  # Второй <p> - это курс продажи

            # Добавляем данные в словарь
            currency_data[currency_name] = {
                'buy_price': buy_price,
                'sell_price': sell_price
            }

    return currency_data

# Пример использования функции
currency_rates = fetch_currency_data_orionbonk()

# Выводим результат
print(currency_rates)
