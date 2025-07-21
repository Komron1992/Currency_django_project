from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    date_of_birth = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date'}))
    phone = forms.CharField(max_length=20, required=False)  # Изменено с phone_number на phone

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'date_of_birth', 'phone', 'password1', 'password2']  # Изменено с phone_number на phone

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autofocus': True}))