from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import (
    CustomUser,
    Currency,
    Bank,
    CurrencyExchangeRate,
    MarketExchangeRate,
    WorkerActivity
)

User = get_user_model()

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительные данные', {
            'fields': ('role', 'city_name', 'phone', 'is_worker_active')  # Изменено с phone_number на phone
        }),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 'role', 'city_name', 'is_staff')  # Изменено с phone_number на phone
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')  # Изменено с phone_number на phone

admin.site.register(User, CustomUserAdmin)
admin.site.register(Currency)
admin.site.register(Bank)
admin.site.register(CurrencyExchangeRate)

@admin.register(MarketExchangeRate)
class MarketExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('currency', 'city_name', 'buy', 'sell', 'date', 'added_by')
    list_filter = ('currency', 'city_name', 'date', 'is_active')
    search_fields = ('city_name', 'currency__code')

@admin.register(WorkerActivity)
class WorkerActivityAdmin(admin.ModelAdmin):
    list_display = ('worker', 'action', 'timestamp')
    list_filter = ('action', 'timestamp')
    readonly_fields = ('timestamp',)