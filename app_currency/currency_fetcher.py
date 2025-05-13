from .eskhata import fetch_and_save_currency_data_eskhata as fetch_eskhata
from .amonatbonk import fetch_and_save_currency_data_amonatbonk as fetch_amonatbonk
from .arvand import fetch_and_save_currency_data_arvand as fetch_arvand
from .imon import fetch_and_save_currency_data_imon as fetch_imon
from .oriyonbonk import fetch_and_save_currency_data_oriyonbonk as fetch_oriyonbonk

def fetch_all_currency_data():
    print("Получение и сохранение данных...")

    try:
        fetch_eskhata()
        print("Данные с Eskhata успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Eskhata: {e}")

    try:
        fetch_arvand()
        print("Данные с Arvand успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Arvand: {e}")

    try:
        fetch_imon()
        print("Данные с Imon успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Imon: {e}")

    try:
        fetch_oriyonbonk()
        print("Данные с Oriyonbonk успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Oriyonbonk: {e}")

    try:
        fetch_amonatbonk()
        print("Данные с Amonatbonk успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Amonatbonk: {e}")
