import json

import django.http
import telebot
from expoBot.service.bot import bot
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import settings


@csrf_exempt
def get_message(request: django.http.HttpRequest):
    if request.method == 'POST':
        json_string = request.body.decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return HttpResponse('!', 200)
    return HttpResponse('Method Not Allowed', 405)


@csrf_exempt
def new_issue(request: django.http.HttpRequest):
    data = json.loads(request.body.decode('utf-8'))
    if assignee_alert(data):
        return HttpResponse('!', 200)
    return HttpResponse('Error', 404)


@csrf_exempt
def issue_state(request: django.http.HttpRequest):
    data = json.loads(request.body.decode('utf-8'))
    if notify(data):
        return HttpResponse('!', 200)
    return HttpResponse('Error', 404)


@csrf_exempt
def new_comment(request: django.http.HttpRequest):
    pass


# bot.set_webhook(url=f'bot.hikmatillo.ru/{settings.BOT_TOKEN}')
