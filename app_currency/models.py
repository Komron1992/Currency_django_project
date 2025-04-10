from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Добавляем дополнительные поля, если нужно
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username

class Currency(models.Model):
    objects = None
    currency = models.CharField(max_length=10, unique=True)
    buy = models.DecimalField(max_digits=10, decimal_places=2)
    sell = models.DecimalField(max_digits=10, decimal_places=2)
    nbt = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.currency

