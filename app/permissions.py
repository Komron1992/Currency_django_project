# app/permissions.py

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Разрешение только для администраторов"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsCityWorker(BasePermission):
    """Разрешение только для городских работников"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'city_worker' and
            request.user.is_worker_active and
            request.user.city_name is not None  # Исправлено: city -> city_name
        )


class IsCityWorkerOrAdmin(BasePermission):
    """Разрешение для работников или админов"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Админы имеют полный доступ
        if request.user.role == 'admin':
            return True

        # Активные работники с назначенным городом
        if (request.user.role == 'city_worker' and
                request.user.is_worker_active and
                request.user.city_name is not None):  # Исправлено: city -> city_name
            return True

        return False


class CanManageOwnCityRates(BasePermission):
    """Разрешение на управление курсами только своего города"""

    def has_permission(self, request, view):
        # Базовая проверка аутентификации
        if not request.user.is_authenticated:
            return False

        # Админы могут управлять курсами любого города
        if request.user.role == 'admin':
            return True

        # Работники могут управлять только курсами своего города
        if (request.user.role == 'city_worker' and
                request.user.is_worker_active and
                request.user.city_name is not None):  # Исправлено: city -> city_name
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # Админы могут управлять любыми курсами
        if request.user.role == 'admin':
            return True

        # Работники могут управлять только курсами своего города
        if (request.user.role == 'city_worker' and
                request.user.is_worker_active and
                request.user.city_name is not None):  # Исправлено: city -> city_name

            # Проверяем, что курс принадлежит городу работника
            if hasattr(obj, 'city_name'):  # Исправлено: city -> city_name
                return obj.city_name == request.user.city_name

            # Если это создание нового курса, проверяем данные запроса
            if request.method == 'POST' and 'city_name' in request.data:  # Исправлено: city -> city_name
                return str(request.data['city_name']) == str(request.user.city_name)

        return False


class IsWorkerOwner(BasePermission):
    """Разрешение для работников управлять только своими курсами"""

    def has_object_permission(self, request, view, obj):
        # Админы могут управлять любыми курсами
        if request.user.role == 'admin':
            return True

        # Работники могут управлять только своими курсами
        if (request.user.role == 'city_worker' and
                hasattr(obj, 'added_by')):
            return obj.added_by == request.user

        return False


class IsReadOnlyOrAuthenticated(BasePermission):
    """Чтение для всех, изменение только для аутентифицированных"""

    def has_permission(self, request, view):
        # Разрешаем чтение всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменения только для аутентифицированных пользователей
        return request.user.is_authenticated


class CanViewCityData(BasePermission):
    """Разрешение на просмотр данных города"""

    def has_permission(self, request, view):
        # Чтение разрешено всем
        if request.method in permissions.SAFE_METHODS:
            return True

        # Изменения только для админов и работников
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'city_worker']
        )


class CanManageWorkers(BasePermission):
    """Разрешение на управление работниками (только админы)"""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


# Вспомогательные функции для проверки разрешений

def can_user_edit_city_rates(user, city_name):  # Исправлено: параметр city -> city_name
    """Проверяет, может ли пользователь редактировать курсы города"""
    if not user.is_authenticated:
        return False

    if user.role == 'admin':
        return True

    if (user.role == 'city_worker' and
            user.is_worker_active and
            user.city_name == city_name):  # Исправлено: city -> city_name
        return True

    return False


def get_user_accessible_cities(user):
    """Возвращает список городов, доступных пользователю"""
    # Поскольку теперь используется city_name как строка, возвращаем список строк
    if not user.is_authenticated:
        return []

    if user.role == 'admin':
        # Админы могут видеть все города - можно вернуть все доступные города
        # Здесь можно подключить функцию загрузки городов из JSON
        from .myviews import load_cities_from_json
        return load_cities_from_json()

    if (user.role == 'city_worker' and
            user.is_worker_active and
            user.city_name):
        return [user.city_name]

    return []


def get_user_accessible_rates(user):
    """Возвращает queryset курсов, доступных пользователю"""
    from .models import MarketExchangeRate

    if not user.is_authenticated:
        return MarketExchangeRate.objects.none()

    if user.role == 'admin':
        return MarketExchangeRate.objects.all()

    if (user.role == 'city_worker' and
            user.is_worker_active and
            user.city_name):  # Исправлено: city -> city_name
        return MarketExchangeRate.objects.filter(city_name=user.city_name)  # Исправлено: city -> city_name

    return MarketExchangeRate.objects.none()