from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Make sure you import your custom user model

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
