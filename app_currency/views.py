from django.shortcuts import render
from .models import Currency  # если у вас есть модель Currency
from .eskhata import fetch_currency_data  # Импортируем функцию парсинга
from .arvand import fetch_currency_data_arvand
from .imon import fetch_currency_data_imon
from .orionbonk import fetch_currency_data_orionbonk

# Представление, которое передает данные из обоих источников в шаблон
def currency_list(request):
    try:
        # Получаем данные с сайта Eskhata
        eskhata_data = fetch_currency_data()
    except Exception as e:
        eskhata_data = None
        print(f"Ошибка при получении данных с Eskhata: {e}")

    try:
        # Получаем данные с сайта Arvand
        arvand_data = fetch_currency_data_arvand()
    except Exception as e:
        arvand_data = None
        print(f"Ошибка при получении данных с Arvand: {e}")

    try:
        # Получаем данные с сайта Imon
        imon_data = fetch_currency_data_imon()
    except Exception as e:
        imon_data = None
        print(f"Ошибка при получении данных с Imon: {e}")

    try:
        # Получаем данные с сайта OrionBonk
        orionbonk_data = fetch_currency_data_orionbonk()
    except Exception as e:
        orionbonk_data = None
        print(f"Ошибка при получении данных с OrionBonk: {e}")

    # Печать всех данных для отладки
    print("Данные с Eskhata:", eskhata_data)
    print("Данные с Arvand:", arvand_data)
    print("Данные с Imon:", imon_data)
    print("Данные с OrionBonk:", orionbonk_data)

    # Передаем данные в шаблон
    return render(request, 'currency_list.html', {
        'data_eskhata': eskhata_data,
        'data_arvand': arvand_data,
        'data_imon': imon_data,
        'data_orionbonk': orionbonk_data
    })
