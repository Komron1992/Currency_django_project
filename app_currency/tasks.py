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
    logger.debug("Задача обновления валюты стартовала")
    try:
        logger.debug("Пытаемся получить данные о валюте...")
        data = fetch_all_currency_data()
        logger.debug("Полученные данные: %s", data)

        if not data:
            logger.error("Не удалось получить данные о валюте.")
            return

        for code in ['usd', 'eur', 'rur']:
            if code in data:
                values = data[code]
                Currency.objects.update_or_create(
                    currency=code.upper(),
                    defaults={
                        'buy': values.get('buy'),
                        'sell': values.get('sell')
                    }
                )
                logger.debug(f"{code.upper()} обновлены: {values}")
            else:
                logger.warning(f"Нет данных по валюте {code.upper()}")

        logger.info("Данные о валюте успешно обновлены")

    except Exception as e:
        logger.error("Ошибка при обновлении курса валют: %s", str(e))
# Создаем объект Celery
app = Celery('currency')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Ставим задачу на выполнение каждую минуту
    sender.add_periodic_task(
        crontab(minute=0, hour='*'),
        update_currency.s(),  # Запускаем задачу
    )
