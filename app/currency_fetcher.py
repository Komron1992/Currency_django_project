from .eskhata import fetch_and_save_currency_data_eskhata
from .amonatbonk import fetch_and_save_currency_data_amonatbonk
from .arvand import fetch_and_save_currency_data_arvand
from .imon import fetch_and_save_currency_data_imon
from .oriyonbonk import fetch_and_save_currency_data_oriyonbonk
from .nbt import fetch_and_save_currency_data_nbt
from .spitamenbank import fetch_and_save_currency_data_spitamenbank
from .humo import fetch_and_save_currency_data_humo
from .azizimoliya import fetch_and_save_currency_data_azizimoliya
from .brt import fetch_and_save_currency_data_brt
from .cbt import fetch_and_save_currency_data_cbt
from .finca import fetch_and_save_currency_data_finca
from .ibt import fetch_and_save_currency_data_ibt
from .matin import fetch_and_save_currency_data_matin
from .ssb import fetch_and_save_currency_data_ssb
from .tawhidbank import fetch_and_save_currency_data_tawhidbank
from .tejaratbank import fetch_and_save_currency_data_tejaratbank

def fetch_all_currency_data():
    print("Получение и сохранение данных...")

    try:
        fetch_and_save_currency_data_nbt()
        print("Данные с NBT успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с NBT: {e}")

    try:
        fetch_and_save_currency_data_eskhata()
        print("Данные с Eskhata успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Eskhata: {e}")

    try:
        fetch_and_save_currency_data_arvand()
        print("Данные с Arvand успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Arvand: {e}")

    try:
        fetch_and_save_currency_data_imon()
        print("Данные с Imon успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Imon: {e}")

    try:
        fetch_and_save_currency_data_oriyonbonk()
        print("Данные с Oriyonbonk успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Oriyonbonk: {e}")

    try:
        fetch_and_save_currency_data_amonatbonk()
        print("Данные с Amonatbonk успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Amonatbonk: {e}")

    try:
        fetch_and_save_currency_data_humo()
        print("Данные с Humo успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Humo: {e}")

    try:
        fetch_and_save_currency_data_azizimoliya()
        print("Данные с Azizimoliya успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Azizimoliya: {e}")

    try:
        fetch_and_save_currency_data_spitamenbank()
        print("Данные с Spitamenbank успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Spitamenbank: {e}")

    try:
        fetch_and_save_currency_data_brt()
        print("Данные с Bonki Rushd успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Bonki Rushd: {e}")

    try:
        fetch_and_save_currency_data_cbt()
        print("Данные с Kommersbank успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Kommersbank: {e}")

    try:
        fetch_and_save_currency_data_finca()
        print("Данные с Finca успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Finca: {e}")

    try:
        fetch_and_save_currency_data_ibt()
        print("Данные с IBT успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с IBT: {e}")

    try:
        fetch_and_save_currency_data_matin()
        print("Данные с Matin успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Matin: {e}")

    try:
        fetch_and_save_currency_data_ssb()
        print("Данные с Sanoatsodirotbonk успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Sanoatsodirotbonk: {e}")


    try:
        fetch_and_save_currency_data_tawhidbank()
        print("Данные с Tawhidbank успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Tawhidbank: {e}")

    try:
        fetch_and_save_currency_data_tejaratbank()
        print("Данные с Tejaratbank успешно обновлены.")
    except Exception as e:
        print(f"Ошибка при получении данных с Tejaratbank: {e}")

    return True  # или dict, если нужно

