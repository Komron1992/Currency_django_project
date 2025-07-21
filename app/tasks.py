from celery import shared_task
from .currency_fetcher import (
    fetch_and_save_currency_data_nbt,
    fetch_and_save_currency_data_eskhata,
    fetch_and_save_currency_data_arvand,
    fetch_and_save_currency_data_imon,
    fetch_and_save_currency_data_oriyonbonk,
    fetch_and_save_currency_data_amonatbonk,
    fetch_and_save_currency_data_spitamenbank,
    fetch_and_save_currency_data_humo,
    fetch_and_save_currency_data_azizimoliya,
    fetch_and_save_currency_data_brt,
    fetch_and_save_currency_data_cbt,
    fetch_and_save_currency_data_finca,
    fetch_and_save_currency_data_ibt,
    fetch_and_save_currency_data_matin,
    fetch_and_save_currency_data_ssb,
    fetch_and_save_currency_data_tawhidbank,
    fetch_and_save_currency_data_tejaratbank,
)
import logging

logger = logging.getLogger('app')

@shared_task
def update_currency():
    funcs = [
        fetch_and_save_currency_data_nbt,
        fetch_and_save_currency_data_eskhata,
        fetch_and_save_currency_data_arvand,
        fetch_and_save_currency_data_imon,
        fetch_and_save_currency_data_oriyonbonk,
        fetch_and_save_currency_data_amonatbonk,
        fetch_and_save_currency_data_spitamenbank,
        fetch_and_save_currency_data_humo,
        fetch_and_save_currency_data_azizimoliya,
        fetch_and_save_currency_data_brt,
        fetch_and_save_currency_data_cbt,
        fetch_and_save_currency_data_finca,
        fetch_and_save_currency_data_ibt,
        fetch_and_save_currency_data_matin,
        fetch_and_save_currency_data_ssb,
        fetch_and_save_currency_data_tawhidbank,
        fetch_and_save_currency_data_tejaratbank,
    ]

    for func in funcs:
        try:
            func()
            logger.info(f"{func.__name__} успешно выполнена.")
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {e}")

