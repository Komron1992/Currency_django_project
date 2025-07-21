from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from app import myviews
from app.serializers import UserSerializer

# Admin API
admin_router = DefaultRouter()
admin_router.register(r'workers', myviews.WorkerViewSet)
admin_router.register(r'users', myviews.UserViewSet, basename='users')
admin_router.register(r'currencies', myviews.CurrencyViewSet)
admin_router.register(r'banks', myviews.BankViewSet)
admin_router.register(r'market-exchange-rates', myviews.MarketExchangeRateViewSet)
admin_router.register(r'worker-activity', myviews.WorkerActivityViewSet)


# Workers
worker_router = DefaultRouter()
worker_router.register(r'rates', myviews.MarketExchangeRateViewSet, basename='worker-rates')
worker_router.register(r'currencies', myviews.WorkerCurrencyViewSet, basename='worker-currencies')

# Public API
public_router = DefaultRouter()
public_router.register(r'bank-rates', myviews.CurrencyExchangeRateViewSet, basename='bank-rates')
# API Root
def api_root(request):
    return JsonResponse({'message': 'Currency Exchange API', 'version': '1.0', 'status': 'active'})

# 🔥 Новый endpoint: /api/auth/user/
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),

    # 🔥 Новые endpoints
    path('api/health/', myviews.health_check, name='health-check'),
    path('api/admin/statistics/', myviews.get_admin_statistics, name='admin-statistics'),
    path('api/cities/', myviews.get_cities, name='get-cities'),

    # Аутентификация
    path('api/auth/login/', myviews.login_view, name='login'),
    path('api/auth/logout/', myviews.logout_view, name='logout'),
    path('api/auth/register/', myviews.register, name='register'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/auth/user/', current_user_view, name='current-user'),  # 🔥

    path('api/admin/', include(admin_router.urls)),
    path('api/workers/', include(worker_router.urls)),
    path('api/public/', include(public_router.urls)),

    path('api/public/rates/', myviews.PublicRatesView.as_view(), name='public-rates'),

    path('', TemplateView.as_view(template_name='admin_vue.html'), name='frontend'),
    path('<path:path>', TemplateView.as_view(template_name='admin_vue.html'), name='frontend-catch-all'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    if hasattr(settings, 'MEDIA_URL') and hasattr(settings, 'MEDIA_ROOT'):
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)