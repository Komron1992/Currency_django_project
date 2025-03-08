from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from app_currency import views # импортируем представления из app_currency

urlpatterns = [
    path('admin/', admin.site.urls),
    path('currencies/', views.currency_list, name='currency_list'), # Главная страница с таблицей
    path('', lambda request: redirect('currency_list')),  # Перенаправление на /currencies/
]

