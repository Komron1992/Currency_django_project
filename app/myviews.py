from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q
import csv
import logging
import json
import os

from .models import (
    CustomUser, Currency, Bank,
    MarketExchangeRate, CurrencyExchangeRate, WorkerActivity
)
from .serializers import (
    UserSerializer, CurrencySerializer, BankSerializer,
    MarketExchangeRateSerializer, CurrencyExchangeRateSerializer,
    WorkerActivitySerializer, CreateWorkerSerializer, WorkerSerializer,
    RegisterSerializer, WorkerMarketRateSerializer
)
from .permissions import IsAdmin, IsCityWorker, CanManageOwnCityRates

logger = logging.getLogger(__name__)


# Загрузка городов из JSON
def load_cities_from_json():
    """Загружает список городов из JSON файла"""
    try:
        # Исправленный путь к файлу
        json_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'public', 'cities.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('cities', [])
    except FileNotFoundError:
        logger.warning("cities.json not found, using default cities")
        return [
            {'id': 1, 'name': 'Душанбе', 'region': 'Душанбе'},
            {'id': 2, 'name': 'Худжанд', 'region': 'Согдийская область'},
            {'id': 3, 'name': 'Истаравшан', 'region': 'Согдийская область'}
        ]
    except Exception as e:
        logger.error(f"Error loading cities: {e}")
        return []


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cities(request):
    """API для получения списка городов"""
    cities = load_cities_from_json()
    return Response({'cities': cities})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_admin_statistics(request):
    """Получение статистики для админ панели"""
    try:
        today = timezone.now().date()

        # Статистика пользователей
        total_users = CustomUser.objects.count()
        admin_users = CustomUser.objects.filter(
            Q(role='admin') | Q(is_superuser=True) | Q(is_staff=True)
        ).count()
        worker_users = CustomUser.objects.filter(role='city_worker').count()
        regular_users = total_users - admin_users - worker_users

        # Статистика городов
        cities = load_cities_from_json()
        total_cities = len(cities)
        cities_with_workers = CustomUser.objects.filter(
            role='city_worker'
        ).values('city_name').distinct().count()

        # Статистика курсов
        today_market_rates = MarketExchangeRate.objects.filter(
            date=today,
            is_active=True
        ).count()

        today_bank_rates = CurrencyExchangeRate.objects.filter(
            date=today,
            is_active=True
        ).count()

        # Статистика активности
        today_activities = WorkerActivity.objects.filter(
            created_at__date=today
        ).count()

        # Формируем ответ
        statistics = {
            'users': {
                'total': total_users,
                'admins': admin_users,
                'workers': worker_users,
                'regular': regular_users
            },
            'cities': {
                'total': total_cities,
                'active': total_cities,
                'with_workers': cities_with_workers
            },
            'rates': {
                'today_market': today_market_rates,
                'today_bank': today_bank_rates,
                'total_today': today_market_rates + today_bank_rates
            },
            'activity': {
                'today_activities': today_activities
            },
            'date': today.isoformat(),
            'timestamp': timezone.now().isoformat()
        }

        return Response(statistics, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error getting admin statistics: {str(e)}", exc_info=True)
        return Response({
            'error': 'Ошибка получения статистики',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'ok',
        'timestamp': timezone.now().isoformat(),
        'version': '1.0',
        'service': 'Currency Exchange API'
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Аутентификация пользователя"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            if not user.is_active:
                return Response({
                    'error': 'Account is disabled'
                }, status=status.HTTP_403_FORBIDDEN)

            # Обновляем last_login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            # Создаем токены
            refresh = RefreshToken.for_user(user)

            # Получаем данные пользователя
            user_data = UserSerializer(user).data

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Выход из системы"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                logger.warning(f"Error blacklisting token: {str(e)}")

        return Response({
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    try:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Устанавливаем роль по умолчанию
            user.role = 'user'
            user.save()

            # Создаем токены
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Получение данных текущего пользователя"""
    try:
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return Response({
            'error': 'Error getting user data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicRatesView(generics.ListAPIView):
    """Публичный доступ к курсам валют"""
    serializer_class = MarketExchangeRateSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return MarketExchangeRate.objects.select_related(
            'currency', 'added_by'
        ).filter(is_active=True).order_by('city_name', 'currency__code')


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        """Фильтрация пользователей"""
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        return queryset.order_by('-date_joined')


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return super().get_queryset().order_by('code')


class WorkerCurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().order_by('code')


class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.filter(is_active=True)
    serializer_class = BankSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return super().get_queryset().order_by('name')


class MarketExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = MarketExchangeRate.objects.select_related('currency', 'added_by').all()
    permission_classes = [IsAuthenticated, CanManageOwnCityRates]

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от роли пользователя"""
        if self.request.user.role == 'city_worker':
            return WorkerMarketRateSerializer
        return MarketExchangeRateSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if user.role == 'admin' or user.is_superuser:
            return queryset.order_by('-date', '-created_at')
        elif user.role == 'city_worker' and user.city_name:
            return queryset.filter(city_name=user.city_name).order_by('-date', '-created_at')
        else:
            return MarketExchangeRate.objects.none()

    def perform_create(self, serializer):
        """Создание курса с учетом роли пользователя"""
        user = self.request.user

        try:
            if user.role == 'city_worker':
                # Для работников автоматически устанавливаем город
                instance = serializer.save(
                    added_by=user,
                    city_name=user.city_name,
                    date=timezone.now().date()
                )
            else:
                # Для админов используем указанный город
                city_name = serializer.validated_data.get('city_name')
                instance = serializer.save(
                    added_by=user,
                    city_name=city_name,
                    date=timezone.now().date()
                )

            # Логирование активности
            if user.role == 'city_worker':
                WorkerActivity.objects.create(
                    worker=user,
                    action='add_rate',
                    description=f'Добавлен курс {instance.currency.code} для города {instance.city_name}',
                    related_rate=instance
                )

        except Exception as e:
            logger.error(f"Error creating market rate: {str(e)}")
            raise


class CurrencyExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = CurrencyExchangeRate.objects.select_related('bank', 'currency').all()
    serializer_class = CurrencyExchangeRateSerializer
    permission_classes = [IsAuthenticated]  # ✅ Для всех авторизованных

    def get_queryset(self):
        return super().get_queryset().order_by('-date', '-created_at')


class WorkerActivityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WorkerActivity.objects.select_related('worker', 'related_rate').all()
    serializer_class = WorkerActivitySerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return super().get_queryset().order_by('-created_at')


class WorkerViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.filter(role='city_worker')
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateWorkerSerializer
        elif self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return WorkerSerializer
        else:
            return UserSerializer

    def get_queryset(self):
        return super().get_queryset().order_by('-date_joined')

    def perform_create(self, serializer):
        """Логирование создания работника"""
        try:
            # Сохраняем объект и получаем его
            worker = serializer.save()  # Здесь мы получаем созданный объект

            # Логирование создания работника
            WorkerActivity.objects.create(
                worker=worker,
                action='created',
                description=f'Работник создан администратором {self.request.user.username}'
            )

        except Exception as e:
            logger.error(f"Error in perform_create: {str(e)}")
            raise

    def perform_update(self, serializer):
        """Логирование обновления работника"""
        try:
            # Сохраняем старые значения ДО обновления
            old_city = serializer.instance.city_name
            old_phone = serializer.instance.phone

            # Обновляем объект
            worker = serializer.save()

            # Проверяем изменения
            changes = []
            if old_city != worker.city_name:
                changes.append(f'город изменен с {old_city} на {worker.city_name}')
            if old_phone != worker.phone:
                changes.append(f'телефон изменен с {old_phone} на {worker.phone}')

            if changes:
                WorkerActivity.objects.create(
                    worker=worker,
                    action='updated',
                    description=f'Данные обновлены: {", ".join(changes)}'
                )

        except Exception as e:
            logger.error(f"Error updating worker: {str(e)}")
            raise

    def create(self, request, *args, **kwargs):
        """Создание нового работника"""
        try:
            serializer = self.get_serializer(data=request.data)

            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Создаем работника через perform_create
            self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )

        except Exception as e:
            logger.error(f"Error creating worker: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Ошибка создания работника: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """Переопределяем метод update для лучшего логирования"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Логируем входящие данные
        logger.info(f"Updating worker {instance.id} ({instance.username})")
        logger.info(f"Request data: {request.data}")
        logger.info(f"Current phone: {instance.phone}")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Выполняем обновление
        self.perform_update(serializer)

        # Получаем обновленные данные
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        # Логируем результат
        logger.info(f"Worker updated successfully. New phone: {instance.phone}")

        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Частичное обновление"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def toggle_active(self, request, pk=None):
        try:
            worker = self.get_object()
            worker.is_worker_active = not worker.is_worker_active
            worker.save(update_fields=['is_worker_active'])

            action = 'activated' if worker.is_worker_active else 'deactivated'
            WorkerActivity.objects.create(
                worker=worker,
                action=action,
                description=f'Работник {action} администратором {request.user.username}'
            )

            return Response({
                'message': f'Работник {"активирован" if worker.is_worker_active else "деактивирован"}',
                'is_worker_active': worker.is_worker_active
            })

        except Exception as e:
            logger.error(f"Error toggling worker active status: {str(e)}")
            return Response(
                {'error': 'Ошибка при изменении статуса работника'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def reset_password(self, request, pk=None):
        try:
            worker = self.get_object()
            new_password = request.data.get('new_password')

            if not new_password or len(new_password) < 8:
                return Response(
                    {'error': 'Пароль должен содержать минимум 8 символов'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            worker.set_password(new_password)
            worker.save(update_fields=['password'])

            WorkerActivity.objects.create(
                worker=worker,
                action='password_reset',
                description=f'Пароль сброшен администратором {request.user.username}'
            )

            return Response({'message': 'Пароль успешно изменен'})

        except Exception as e:
            logger.error(f"Error resetting worker password: {str(e)}")
            return Response(
                {'error': 'Ошибка при сбросе пароля'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # Дополнительный метод для тестирования обновления телефона
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def update_phone(self, request, pk=None):
        """Специальный метод для обновления только телефона"""
        try:
            worker = self.get_object()
            new_phone = request.data.get('phone')

            if new_phone is None:
                return Response(
                    {'error': 'Поле phone обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            old_phone = worker.phone
            worker.phone = new_phone
            worker.save(update_fields=['phone'])

            # Обновляем из базы данных
            worker.refresh_from_db()

            logger.info(f"Phone updated: {old_phone} -> {worker.phone}")

            # Логируем активность
            WorkerActivity.objects.create(
                worker=worker,
                action='phone_updated',
                description=f'Телефон изменен с {old_phone} на {worker.phone}'
            )

            return Response({
                'message': 'Телефон успешно обновлен',
                'old_phone': old_phone,
                'new_phone': worker.phone
            })

        except Exception as e:
            logger.error(f"Error updating phone: {str(e)}")
            return Response(
                {'error': 'Ошибка при обновлении телефона'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )