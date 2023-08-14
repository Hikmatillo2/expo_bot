from django.contrib import admin
from .forms import *


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'telegram_id',
        'nickname',
        'first_name',
        'second_name',
        'email',
        'phone_number',
    ]

    form = BotUserForm


@admin.register(BotUserCondition)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'on_first_name_input',
        'on_second_name_input',
        'on_email_input',
        'on_phone_number_input',
    ]

@admin.register(File)
class BotUserAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'file',
    ]
