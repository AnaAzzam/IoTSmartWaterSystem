
from django import forms
from django.contrib.auth.forms import UserCreationForm
from core.models.base import CustomUser

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        required=False,
        max_length=13,
        help_text="Optional: Enter phone number in the format +20XXXXXXXXXX (e.g., +201234567890)"
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'phone_number', 'password1', 'password2')
