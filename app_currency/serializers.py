from rest_framework import serializers
from .models import Bank, Currency, ExchangeRate


class BankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bank
        fields = ['id', 'name']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code']


class ExchangeRateSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source='currency.code')
    bank = serializers.CharField(source='bank.name')
    buy = serializers.SerializerMethodField()
    sell = serializers.SerializerMethodField()

    class Meta:
        model = ExchangeRate
        fields = ['id', 'currency', 'bank', 'buy', 'sell', 'updated_at', 'created_at']

    def get_buy(self, obj):
        return float(obj.buy)

    def get_sell(self, obj):
        return float(obj.sell)
