from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Currency, ExchangeRate

User = get_user_model()
admin.site.register(User, UserAdmin)
admin.site.register(Currency)
admin.site.register(ExchangeRate)