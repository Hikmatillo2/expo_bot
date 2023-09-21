from django.contrib import admin
from .forms import *


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id',
        'api_id',
        'api_hash',
        'phone_number',
    ]


@admin.register(BotUserCondition)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'on_api_id_input',
        'on_api_hash_input',
        'on_phone_number_input',
    ]


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = [
        'entity'
    ]
