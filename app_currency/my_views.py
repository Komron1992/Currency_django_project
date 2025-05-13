from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .forms import CustomLoginForm  # Импортируйте вашу форму
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from .models import ExchangeRate, Bank, Currency  # если у вас есть модель Currency
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import CurrencySerializer, BankSerializer, ExchangeRateSerializer
from rest_framework import viewsets
from django.http import JsonResponse
from .currency_fetcher import fetch_all_currency_data
from django.core.cache import cache
from django.core.cache import cache

# Функция для получения и сохранения данных валют с разных источников
def currency_data_view(request):
    try:
        # Получаем и сохраняем данные со всех источников
        fetch_all_currency_data()

        # ❗ Очищаем кеш после обновления данных
        cache.delete('exchange_rates_by_bank')

        # Получаем данные из базы
        currencies = Currency.objects.all()
        data = CurrencySerializer(currencies, many=True).data
        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Представление для отображения данных с разных источников
@login_required
def currency_list(request):
    banks = Bank.objects.all()
    data = {}

    for bank in banks:
        rates = ExchangeRate.objects.filter(bank=bank).select_related('currency').order_by('currency__code')
        if rates.exists():
            bank_data = {}
            for rate in rates:
                bank_data[rate.currency.code] = {
                    'buy': rate.buy,
                    'sell': rate.sell
                }
            data[bank.name] = bank_data  # Используем name, а не code
        else:
            data[bank.name] = None

    return render(request, 'currency_list.html', {'data': data})

# Представление для регистрации нового пользователя
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            print("Форма валидна, сохраняем пользователя")
            form.save()
            return redirect('login')  # После регистрации редиректим на страницу входа
        else:
            print("Форма не валидна")
            print(form.errors)  # Вывод ошибок формы для диагностики
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

# Представление для входа пользователя
def custom_login(request):
    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            # Если форма валидна, аутентифицируем пользователя и выполняем вход
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/currencies/')  # Перенаправление после входа
            else:
                form.add_error(None, "Неверное имя пользователя или пароль.")
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

# Пример защищённого представления
class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view!"})

# Представление для получения списка валют
class CurrencyList(APIView):
    def get(self, request):
        currencies = Currency.objects.all()  # Получаем все валюты
        serializer = CurrencySerializer(currencies, many=True)  # Сериализуем
        return Response(serializer.data)

    def post(self, request):
        serializer = CurrencySerializer(data=request.data)  # Получаем данные из запроса
        if serializer.is_valid():
            serializer.save()  # Сохраняем валюту
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ViewSet для валют
class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

# Новый API для отображения валютных курсов с форматированием
class ExchangeRateFormattedView(APIView):
    def get(self, request):
        # Получаем данные из базы данных (ExchangeRate)
        rates = ExchangeRate.objects.all().select_related('currency', 'bank').order_by('currency__code', 'bank__name')

        # Проверяем, если данные есть
        if not rates:
            return Response({"message": "No exchange rates found in the database"}, status=status.HTTP_404_NOT_FOUND)

        # Форматируем данные для вывода
        formatted = []
        for item in rates:
            currency = item.currency.code  # Например, USD
            buy = item.buy  # Цена покупки
            sell = item.sell  # Цена продажи
            bank = item.bank.name  # Название банка
            line = f"{currency} — buy: {buy}, sell: {sell}, Source: {bank}"
            formatted.append(line)

        # Возвращаем данные в нужном формате
        return Response({
            "message": "Exchange rates of all banks",
            "data": formatted
        })


# Новый API: Курсы валют по банкам в формате словаря
class ExchangeRatesByBankView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cache_key = 'exchange_rates_by_bank'
        data = cache.get(cache_key)

        if not data:
            print("🔄 Получаем данные из базы...")
            banks = Bank.objects.all()
            result = {}

            for bank in banks:
                rates = ExchangeRate.objects.filter(bank=bank).select_related('currency')
                if rates.exists():
                    currency_data = {
                        rate.currency.code: {
                            "buy": rate.buy,
                            "sell": rate.sell
                        }
                        for rate in rates
                    }
                    result[bank.name] = currency_data
                else:
                    result[bank.name] = None

            data = result
            cache.set(cache_key, data, timeout=3600)  # кешируем на 1 час

        else:
            print("✅ Данные из кеша")

        return Response(data)

class BankViewSet(viewsets.ModelViewSet):
    queryset = Bank.objects.all()
    serializer_class = BankSerializer

class ExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRate.objects.all().select_related('currency', 'bank')
    serializer_class = ExchangeRateSerializer