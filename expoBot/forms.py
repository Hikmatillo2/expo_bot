from django import forms
from .models import *


class BotUserForm(forms.ModelForm):
    class Meta:
        model = BotUser
        fields = (
            'telegram_id',
            'nickname',
            'first_name',
            'second_name',
            'email',
            'phone_number',
        )

        widgets = {
            'first_name': forms.TextInput,
            'nickname': forms.TextInput,
            'second_name': forms.TextInput,
            'email': forms.EmailInput,
            'phone_number': forms.TextInput,
        }
