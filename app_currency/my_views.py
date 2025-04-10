from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from .forms import CustomLoginForm  # Импортируйте вашу форму
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Currency  # если у вас есть модель Currency
from .eskhata import fetch_currency_data  # Импортируем функцию парсинга
from .arvand import fetch_currency_data_arvand
from .imon import fetch_currency_data_imon
from .orionbonk import fetch_currency_data_orionbonk
from .amonatbonk import fetch_currency_data_amonatbonk
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import CurrencySerializer
from rest_framework import viewsets
from django.http import JsonResponse
from .currency_fetcher import fetch_all_currency_data

def currency_data_view(request):
    # Получаем данные
    data = fetch_all_currency_data()

    if data:
        return JsonResponse(data)
    else:
        return JsonResponse({"detail": "Не удалось получить данные."}, status=500)

# Представление, которое передает данные из обоих источников в шаблон
@login_required
def currency_list(request):
    try:
        # Получаем данные с сайта Eskhata
        eskhata_data = fetch_currency_data()
    except Exception as e:
        eskhata_data = None
        print(f"Ошибка при получении данных с Eskhata: {e}")

    try:
        # Получаем данные с сайта Arvand
        arvand_data = fetch_currency_data_arvand()
    except Exception as e:
        arvand_data = None
        print(f"Ошибка при получении данных с Arvand: {e}")

    try:
        # Получаем данные с сайта Imon
        imon_data = fetch_currency_data_imon()
    except Exception as e:
        imon_data = None
        print(f"Ошибка при получении данных с Imon: {e}")

    try:
        # Получаем данные с сайта OrionBonk
        orionbonk_data = fetch_currency_data_orionbonk()
    except Exception as e:
        orionbonk_data = None
        print(f"Ошибка при получении данных с OrionBonk: {e}")

    try:
        # Получаем данные с сайта OrionBonk
        amonatbonk_data = fetch_currency_data_amonatbonk()
    except Exception as e:
        amonatbonk_data = None
        print(f"Ошибка при получении данных с OrionBonk: {e}")

    # Печать всех данных для отладки
    print("Данные с Eskhata:", eskhata_data)
    print("Данные с Arvand:", arvand_data)
    print("Данные с Imon:", imon_data)
    print("Данные с OrionBonk:", orionbonk_data)
    print("Данные с Amonatbonk:", amonatbonk_data)

    # Передаем данные в шаблон
    return render(request, 'currency_list.html', {
        'data_eskhata': eskhata_data,
        'data_arvand': arvand_data,
        'data_imon': imon_data,
        'data_orionbonk': orionbonk_data,
        'data_amonatbonk': amonatbonk_data
    })


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

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view!"})

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

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer