from django import forms
from .models import *


class BotUserForm(forms.ModelForm):
    class Meta:
        model = BotUser
        fields = (
            'telegram_id',
            'api_id',
            'api_hash',
        )

        widgets = {
            'api_id': forms.TextInput,
            'api_hash': forms.TextInput,
        }
