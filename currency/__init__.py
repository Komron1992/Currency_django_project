from __future__ import absolute_import, unicode_literals

# Это позволяет использовать Celery при запуске проекта
from .my_celery import app as celery_app

__all__ = ('celery_app',)
