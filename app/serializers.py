# app/serializers.py

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging
import json
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from .models import (
    CustomUser, Currency, Bank,
    CurrencyExchangeRate, MarketExchangeRate, WorkerActivity
)


class CustomDateTimeField(serializers.DateTimeField):
    """Кастомное поле для отображения даты и времени"""

    def to_representation(self, value):
        if value:
            # Если Django настроен правильно, localtime() вернет время в нужной зоне
            local_time = timezone.localtime(value)
            return local_time.strftime('%Y-%m-%d %H:%M:%S')
        return None


def get_local_time():
    """Получение текущего времени в локальной временной зоне"""
    try:
        return timezone.localtime(timezone.now())
    except Exception as e:
        logger.error(f"Error getting local time: {e}")
        return timezone.now()


def load_cities_from_json():
    """Загружает список городов из JSON файла"""
    try:
        json_path = os.path.join(os.path.dirname(__file__), 'cities.json')
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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT-токенов с обновлением last_login"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Обновляем last_login при получении токена (время в локальной зоне)
        current_time = get_local_time()
        user.last_login = current_time
        user.save(update_fields=['last_login'])

        # Обновляем user снова после сохранения
        user.refresh_from_db()

        # Добавляем дополнительные данные в токен
        token['username'] = user.username
        token['role'] = user.role
        token['user_id'] = user.id
        token['last_login'] = current_time.strftime('%Y-%m-%d %H:%M:%S')

        return token

    def validate(self, attrs):
        """Валидация с дополнительными проверками"""
        data = super().validate(attrs)

        # Получаем пользователя
        user = self.user

        # Проверяем, активен ли пользователь
        if not user.is_active:
            raise serializers.ValidationError('Учетная запись отключена')

        # Для работников проверяем, активен ли их статус
        if user.role == 'city_worker' and not user.is_worker_active:
            raise serializers.ValidationError('Статус работника неактивен')

        # Обновляем last_login еще раз для уверенности (время в локальной зоне)
        current_time = get_local_time()
        user.last_login = current_time
        user.save(update_fields=['last_login'])
        user.refresh_from_db()

        # Добавляем информацию о пользователе в ответ
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'role': user.role,
            'role_display': user.get_role_display(),
            'city_name': user.city_name,
            'is_worker_active': user.is_worker_active,
            'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None,
            'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else None,
        }

        return data


class CurrencySerializer(serializers.ModelSerializer):
    """Сериализатор для валют"""

    class Meta:
        model = Currency
        fields = '__all__'


class BankSerializer(serializers.ModelSerializer):
    """Сериализатор для банков"""

    class Meta:
        model = Bank
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор пользователя"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    password = serializers.CharField(write_only=True, min_length=8, required=False)
    last_login = CustomDateTimeField(read_only=True)
    date_joined = CustomDateTimeField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'phone',
            'role', 'role_display', 'city_name',
            'is_worker_active', 'is_superuser',
            'date_joined', 'last_login', 'password'
        ]
        read_only_fields = ['date_joined', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """Создание пользователя с правильным хешированием пароля"""
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def update(self, instance, validated_data):
        """Обновление пользователя с правильным хешированием пароля"""
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance


class WorkerSerializer(serializers.ModelSerializer):
    """Сериализатор для работников"""
    added_rates_count = serializers.SerializerMethodField()
    last_activity = serializers.SerializerMethodField()
    last_login = CustomDateTimeField(read_only=True)
    date_joined = CustomDateTimeField(read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone',
            'city_name', 'is_worker_active', 'date_joined', 'last_login',
            'added_rates_count', 'last_activity', 'password'
        ]
        read_only_fields = ['date_joined', 'last_login', 'added_rates_count', 'last_activity']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_added_rates_count(self, obj):
        """Получение количества добавленных курсов за сегодня"""
        try:
            # Получаем сегодняшнюю дату в локальной зоне
            local_today = get_local_time().date()

            # ИСПРАВЛЕНО: Используем правильный related_name или прямой запрос
            # Вместо obj.added_rates используем обратный запрос к MarketExchangeRate
            return MarketExchangeRate.objects.filter(
                added_by=obj,
                date=local_today
            ).count()
        except Exception as e:
            logger.error(f"Error getting added_rates_count for user {obj.id}: {e}")
            return 0

    def get_last_activity(self, obj):
        """Получение последней активности работника"""
        try:
            # ИСПРАВЛЕНО: Используем правильное поле для сортировки
            last_activity = obj.activities.order_by('-timestamp').first()
            if last_activity:
                return {
                    'action': last_activity.action,
                    'timestamp': last_activity.timestamp.strftime(
                        '%Y-%m-%d %H:%M:%S') if last_activity.timestamp else None,
                    'description': last_activity.description
                }
            return None
        except Exception as e:
            logger.error(f"Error getting last_activity for user {obj.id}: {e}")
            return None

    def update(self, instance, validated_data):
        """Обновление работника с правильным хешированием пароля"""
        password = validated_data.pop('password', None)

        # Логируем данные для отладки
        logger.info(f"Updating worker {instance.username} with data: {validated_data}")
        logger.info(f"Phone before update: {instance.phone}")
        logger.info(f"New phone value: {validated_data.get('phone', 'NOT_PROVIDED')}")

        for attr, value in validated_data.items():
            logger.info(f"Setting {attr} = {value}")
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        logger.info(f"Worker {instance.username} updated successfully. Phone: {instance.phone}")

        return instance


class CreateWorkerSerializer(serializers.ModelSerializer):
    """Сериализатор для создания работников"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone',
            'city_name', 'is_worker_active', 'password', 'password_confirm'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        """Валидация данных"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Пароли не совпадают'
            })

        # Проверяем, что город существует в списке городов
        city_name = attrs.get('city_name')
        if city_name:
            cities = load_cities_from_json()
            city_names = [city['name'] for city in cities]
            if city_name not in city_names:
                raise serializers.ValidationError({
                    'city_name': f'Город "{city_name}" не найден в списке доступных городов'
                })

        return attrs

    def create(self, validated_data):
        """Создание нового работника"""
        # Убираем password_confirm из данных
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        # Логируем данные для отладки
        logger.info(f"Creating worker with data: {validated_data}")
        logger.info(f"Phone in validated_data: {validated_data.get('phone', 'NOT_SET')}")

        # Создаем пользователя
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', ''),
            city_name=validated_data.get('city_name', ''),
            is_worker_active=validated_data.get('is_worker_active', True),
            role='city_worker'
        )

        logger.info(f"Worker created successfully. ID: {user.id}, Phone: {user.phone}")

        return user


# Дополнительный сериализатор для обновления только основных полей
class WorkerUpdateSerializer(serializers.ModelSerializer):
    """Специальный сериализатор для обновления основных полей работника"""

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'city_name', 'is_worker_active'
        ]

    def update(self, instance, validated_data):
        """Простое обновление без лишней логики"""
        # Логируем для отладки
        logger.info(f"WorkerUpdateSerializer: Updating {instance.username}")
        logger.info(f"Data: {validated_data}")

        # Обновляем поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        instance.refresh_from_db()

        logger.info(f"Updated successfully. Phone: {instance.phone}")
        return instance


class MarketExchangeRateSerializer(serializers.ModelSerializer):
    """Сериализатор для рыночных курсов валют"""
    currency_code = serializers.CharField(source='currency.code', read_only=True)
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.username', read_only=True)

    class Meta:
        model = MarketExchangeRate
        fields = ['id', 'currency', 'currency_code', 'currency_name', 'city_name',
                  'buy', 'sell', 'date', 'time', 'added_by', 'added_by_name', 'is_active', 'notes']
        read_only_fields = ['date', 'time', 'added_by']


class WorkerMarketRateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления курсов работниками"""
    currency_code = serializers.CharField(source='currency.code', read_only=True)

    class Meta:
        model = MarketExchangeRate
        fields = ['id', 'currency', 'currency_code', 'buy', 'sell', 'date', 'time', 'notes']
        read_only_fields = []

    def validate(self, attrs):
        """Валидация данных курса"""
        buy = attrs.get('buy')
        sell = attrs.get('sell')

        # Проверяем, что курсы положительные
        if buy and buy <= 0:
            raise serializers.ValidationError({"buy": "Курс покупки должен быть положительным числом"})

        if sell and sell <= 0:
            raise serializers.ValidationError({"sell": "Курс продажи должен быть положительным числом"})

        # Проверяем, что курс покупки меньше курса продажи
        if buy and sell and buy >= sell:
            raise serializers.ValidationError({"buy": "Курс покупки должен быть меньше курса продажи"})

        return attrs

    def validate_currency(self, value):
        """Проверка валюты"""
        if not value:
            raise serializers.ValidationError("Необходимо выбрать валюту")

        if not value.is_active:
            raise serializers.ValidationError("Выбранная валюта неактивна")

        return value

    def create(self, validated_data):
        """Создание курса с автоматическим добавлением города и пользователя"""
        request = self.context.get('request')
        user = request.user

        # Проверяем права пользователя
        if user.role != 'city_worker':
            raise serializers.ValidationError("Только работники могут добавлять курсы через этот endpoint")

        if not user.city_name:
            raise serializers.ValidationError("У пользователя не указан город")

        if not user.is_worker_active:
            raise serializers.ValidationError("Аккаунт работника неактивен")

        # Добавляем обязательные поля
        validated_data['city_name'] = user.city_name
        validated_data['added_by'] = user
        validated_data['is_active'] = True

        # Устанавливаем время в локальной временной зоне
        current_time = get_local_time()
        validated_data['date'] = current_time.date()
        validated_data['time'] = current_time.time()

        print(f"🕐 [DEBUG] Создание курса с локальным временем: {current_time.date()} {current_time.time()}")

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Обновление курса с ПРИНУДИТЕЛЬНЫМ обновлением времени в локальной зоне"""
        # ПРИНУДИТЕЛЬНО обновляем время на текущее в локальной зоне
        current_time = get_local_time()

        print(f"🕐 [DEBUG] Обновление времени курса ID {instance.id}")
        print(f"🕐 [DEBUG] Старое время: {instance.date} {instance.time}")
        print(f"🕐 [DEBUG] Новое время (локальное): {current_time.date()} {current_time.time()}")

        # Обновляем время
        instance.date = current_time.date()
        instance.time = current_time.time()

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            if attr not in ['date', 'time']:  # Время мы уже установили
                setattr(instance, attr, value)

        # Сохраняем изменения
        instance.save()

        print(f"✅ [DEBUG] Курс сохранен. Время в БД: {instance.date} {instance.time}")

        return instance


class CurrencyExchangeRateSerializer(serializers.ModelSerializer):
    """Сериализатор для банковских курсов"""
    bank_name = serializers.CharField(source='bank.name', read_only=True)
    currency_code = serializers.CharField(source='currency.code', read_only=True)

    class Meta:
        model = CurrencyExchangeRate
        fields = ['id', 'bank', 'bank_name', 'currency', 'currency_code', 'buy', 'sell', 'date', 'time']


class WorkerActivitySerializer(serializers.ModelSerializer):
    """Сериализатор для активности работников"""
    worker_name = serializers.CharField(source='worker.username', read_only=True)
    city_name = serializers.CharField(source='worker.city_name', read_only=True)
    timestamp = CustomDateTimeField(read_only=True)

    class Meta:
        model = WorkerActivity
        fields = ['id', 'worker', 'worker_name', 'city_name', 'action', 'description', 'timestamp']


class CityRatesSerializer(serializers.Serializer):
    """Сериализатор для отображения курсов по городам"""
    city_name = serializers.CharField()
    rates = MarketExchangeRateSerializer(many=True)


class AssignWorkerSerializer(serializers.Serializer):
    """Сериализатор для назначения работника на город"""
    worker_id = serializers.IntegerField()
    city_name = serializers.CharField()

    def validate_worker_id(self, value):
        try:
            worker = CustomUser.objects.get(id=value, role='city_worker')
            return value
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Работник не найден")

    def validate_city_name(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо указать название города")

        # Проверяем, что город существует в списке городов
        cities = load_cities_from_json()
        city_names = [city['name'] for city in cities]
        if value not in city_names:
            raise serializers.ValidationError(f"Город '{value}' не найден в списке доступных городов")

        return value


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа"""
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                raise serializers.ValidationError('Неверные учетные данные')

            if not user.is_active:
                raise serializers.ValidationError('Учетная запись отключена')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Необходимо указать имя пользователя и пароль')


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm']

    def validate_username(self, value):
        """Проверка уникальности username"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value

    def validate_email(self, value):
        """Проверка уникальности email"""
        if value and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate_phone(self, value):
        """Проверка уникальности телефона"""
        if value and CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Пользователь с таким номером телефона уже существует")
        return value

    def validate(self, attrs):
        """Общая валидация"""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """Создание пользователя с правильным хешированием пароля"""
        # Удаляем password_confirm из данных
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')

        # Создаем пользователя БЕЗ пароля
        user = CustomUser.objects.create(**validated_data)

        # Устанавливаем пароль через set_password для правильного хеширования
        user.set_password(password)
        user.save()

        return user