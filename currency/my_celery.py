from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите правильное название Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'currency.settings')

app = Celery('currency')

# Используйте строку подключения для Redis
app.config_from_object('django.conf:settings', namespace='CELERY')

# Задачи Celery
app.autodiscover_tasks()

app.conf.update(
    broker_url='redis://localhost:6379/0',  # Используем локальный Redis
    result_backend='redis://localhost:6379/0',  # Храним результаты в Redis
)
