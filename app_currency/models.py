from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username


class Bank(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)  # Код валюты, например 'USD'

    class Meta:
        db_table = 'app_currency'  # Указываем другое имя таблицы, например 'app_currency'

    def __str__(self):
        return self.code

class ExchangeRate(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    buy = models.DecimalField(max_digits=10, decimal_places=4)
    sell = models.DecimalField(max_digits=10, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_currency_exchangerate'  # Имя таблицы для ExchangeRate

    def __str__(self):
        return f"{self.currency.code} - {self.bank.name}"
