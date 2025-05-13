from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from django.contrib.auth.views import LogoutView

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt import views as jwt_views
from rest_framework.authtoken import views as drf_auth_views

from app_currency import my_views
from app_currency.my_views import (
    custom_login,
    currency_data_view,
    ProtectedView,
    CurrencyViewSet,
    BankViewSet,
    ExchangeRateViewSet,
    ExchangeRateFormattedView,
    ExchangeRatesByBankView,
)

# Роутер DRF для ViewSet'ов
router = DefaultRouter()
router.register(r'currencies', CurrencyViewSet, basename='currency')
router.register(r'banks', BankViewSet, basename='bank')
router.register(r'exchange-rates', ExchangeRateViewSet, basename='exchange-rate')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Веб-интерфейс
    path('currencies/', my_views.currency_list, name='currency_list'),
    path('', lambda request: redirect('currency_list')),

    # Аутентификация
    path('register/', my_views.register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # JWT
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    # Token auth
    path('api-token-auth/', drf_auth_views.obtain_auth_token),

    # Защищённый пример
    path('protected-view/', ProtectedView.as_view(), name='protected-view'),

    # API: ручной парсинг
    path('api/fetch-currency/', currency_data_view, name='currency_data'),

    # API: форматированный список курсов
    path('api/exchange-formatted/', ExchangeRateFormattedView.as_view(), name='exchange-rate-list'),

    # API: курсы по банкам (словари)
    path('api/exchange-by-bank/', ExchangeRatesByBankView.as_view(), name='bank-exchange-rates'),

    # API: ViewSet'ы
    path('api/', include(router.urls)),
]
