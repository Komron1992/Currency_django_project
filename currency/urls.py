from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin
from app_currency import my_views  # импортируем представления из app_currency
from app_currency.my_views import custom_login
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt import views as jwt_views
from app_currency.my_views import ProtectedView
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter
from app_currency.my_views import CurrencyViewSet
from app_currency.my_views import currency_data_view


#router = DefaultRouter()
#router.register(r'currencies', CurrencyViewSet)  # Регистрация ViewSet

urlpatterns = [
    path('admin/', admin.site.urls),
    path('currencies/', my_views.currency_list, name='currency_list'),  # Главная страница с таблицей
    path('', lambda request: redirect('currency_list')),  # Перенаправление на /currencies/
    path('register/', my_views.register, name='register'),
    path('login/', custom_login, name='login'),  # Создайте свою собственную страницу входа
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('protected-view/', ProtectedView.as_view(), name='protected-view'),
    path('api-token-auth/', views.obtain_auth_token),
    #path('api/', include(router.urls)),  # Включаем все маршруты от ViewSet
    path('api/currencies/', currency_data_view, name='currency_data'),
]
