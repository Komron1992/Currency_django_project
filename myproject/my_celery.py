from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


# Установка настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery('myproject')

# Загрузка конфигурации из Django settings (начиная с префикса CELERY)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически искать задачи в файлах tasks.py всех приложений
app.autodiscover_tasks()



