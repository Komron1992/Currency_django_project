from celery import shared_task
import logging
from .currency_fetcher import fetch_all_currency_data
from .models import Currency
from celery import Celery
from celery.schedules import crontab

# Используем логгер для вашего приложения
logger = logging.getLogger('app_currency')

@shared_task
def update_currency():
    logger.debug("Задача обновления валюты стартовала")  # Логирование начала
    try:
        logger.debug("Задача: пытаемся получить данные о валюте...")
        data = fetch_all_currency_data()  # Вызов парсера
        logger.debug("Данные о валюте получены: %s", data)

        if not data:
            logger.error("Не удалось получить данные о валюте.")
            return

        # Обновление данных в базе данных
        logger.debug("Обновление данных для USD...")
        currency_usd = Currency.objects.update_or_create(
            currency='USD',
            defaults={'buy': data['usd']['buy'], 'sell': data['usd']['sell'], 'nbt': data['usd']['nbt']}
        )
        logger.debug("USD обновлены: %s", currency_usd)

        # То же для других валют...
        logger.debug("Обновление данных для EUR...")
        currency_eur = Currency.objects.update_or_create(
            currency='EUR',
            defaults={'buy': data['eur']['buy'], 'sell': data['eur']['sell'], 'nbt': data['eur']['nbt']}
        )
        logger.debug("EUR обновлены: %s", currency_eur)

        logger.debug("Обновление данных для RUR...")
        currency_rur = Currency.objects.update_or_create(
            currency='RUR',
            defaults={'buy': data['rur']['buy'], 'sell': data['rur']['sell'], 'nbt': data['rur']['nbt']}
        )
        logger.debug("RUR обновлены: %s", currency_rur)

        logger.info("Данные о валюте успешно обновлены")
    except Exception as e:
        logger.error("Ошибка при обновлении курса валют: %s", str(e))

# Создаем объект Celery
app = Celery('currency')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Ставим задачу на выполнение каждую минуту
    sender.add_periodic_task(
        crontab(minute='*'),
        update_currency.s(),  # Запускаем задачу
    )
