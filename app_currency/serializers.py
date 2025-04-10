from rest_framework import serializers
from .models import Currency  # Импортируем вашу модель

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['currency', 'buy', 'sell', 'nbt']