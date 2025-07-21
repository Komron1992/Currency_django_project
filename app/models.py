# app/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с ролями"""
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('city_worker', 'City Worker'),  # Новая роль для городских работников
    ]

    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='user'
    )

    # Привязка к городу (для работников) - теперь по названию
    city_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Город, за который отвечает работник"
    )

    # Активность работника
    is_worker_active = models.BooleanField(
        default=True,
        help_text="Может ли работник добавлять курсы"
    )

    # Простое поле телефона без валидации
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Номер телефона"
    )

    def __str__(self):
        if self.city_name and self.role == 'city_worker':
            return f"{self.username} ({self.city_name})"
        return f"{self.username} ({self.get_role_display()})"

    def can_edit_city_rates(self, city_name):
        """Проверяет, может ли пользователь редактировать курсы города"""
        if self.role == 'admin':
            return True
        if self.role == 'city_worker' and self.city_name == city_name and self.is_worker_active:
            return True
        return False


class Currency(models.Model):
    """Модель валюты"""
    code = models.CharField(max_length=3, unique=True)  # USD, EUR, RUB
    name = models.CharField(max_length=50)  # US Dollar, Euro, Russian Ruble
    symbol = models.CharField(max_length=5, blank=True)  # $, €, ₽
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"


class Bank(models.Model):
    """Модель банка"""
    name = models.CharField(max_length=100, unique=True)
    short_name = models.CharField(max_length=20, blank=True)
    icon = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Банк"
        verbose_name_plural = "Банки"


class CurrencyExchangeRate(models.Model):
    """Модель курса валют банков"""
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='rates')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    buy = models.DecimalField(max_digits=10, decimal_places=4)
    sell = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # Добавляем поле is_active
    created_at = models.DateTimeField(auto_now_add=True)  # Добавляем для сортировки

    def __str__(self):
        return f"{self.bank.name} - {self.currency.code}: {self.buy}/{self.sell}"

    class Meta:
        verbose_name = "Курс банка"
        verbose_name_plural = "Курсы банков"
        ordering = ['-date', '-time']


class MarketExchangeRate(models.Model):
    """Модель рыночного курса валют по городам"""
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    city_name = models.CharField(max_length=100, help_text="Название города")
    buy = models.DecimalField(max_digits=10, decimal_places=4)
    sell = models.DecimalField(max_digits=10, decimal_places=4)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Добавляем для сортировки

    # Кто добавил курс
    added_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='added_rates',
        help_text="Пользователь, который добавил курс"
    )

    # Статус курса
    is_active = models.BooleanField(default=True)

    # Дополнительная информация
    notes = models.TextField(blank=True, help_text="Дополнительные заметки")

    def __str__(self):
        return f"{self.city_name} - {self.currency.code}: {self.buy}/{self.sell} ({self.date})"

    def clean(self):
        """Валидация модели"""
        from django.core.exceptions import ValidationError

        # Проверяем, что пользователь может добавлять курсы для этого города
        if self.added_by and not self.added_by.can_edit_city_rates(self.city_name):
            raise ValidationError(
                f"Пользователь {self.added_by.username} не может добавлять курсы для города {self.city_name}"
            )

        # Проверяем корректность курсов
        if self.buy <= 0 or self.sell <= 0:
            raise ValidationError("Курсы должны быть положительными числами")

        if self.buy >= self.sell:
            raise ValidationError("Курс покупки должен быть меньше курса продажи")

    class Meta:
        verbose_name = "Рыночный курс"
        verbose_name_plural = "Рыночные курсы"
        ordering = ['-date', '-time']

        # Убираем unique_together, так как оно может вызывать проблемы
        # unique_together = ['currency', 'city_name', 'date', 'is_active']


class WorkerActivity(models.Model):
    """Модель для отслеживания активности работников"""
    worker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'city_worker'},
        related_name='activities'
    )
    action = models.CharField(max_length=50)  # 'add_rate', 'update_rate', 'delete_rate'
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # Связанные объекты
    related_rate = models.ForeignKey(
        MarketExchangeRate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.worker.username} - {self.action} ({self.timestamp})"

    class Meta:
        verbose_name = "Активность работника"
        verbose_name_plural = "Активность работников"
        ordering = ['-timestamp']