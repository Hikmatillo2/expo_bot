import settings
from expoBot.service.utils.database import *
from expoBot.service.utils.utils import check_user_message, parse_excel, get_info
from expoBot.service.utils.texts import TEXTS
from telebot import TeleBot
from telebot.types import Message

bot = TeleBot(settings.BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start_command(message: Message):
    chat_id = str(message.chat.id)

    # Проверка на то, существует ли пользователь в базе
    if not check_user_exists(chat_id):
        add_user(chat_id, str(message.from_user.username))

    bot.send_message(
        chat_id,
        TEXTS['/start'][0] + TEXTS['instruction'][0],
        parse_mode='html',
    )

    user = get_user_by_id(chat_id)
    user_condition = BotUserCondition.objects.filter(user=user)[0]
    user_condition.on_api_id_input = True
    user_condition.save()


@bot.message_handler(content_types=['document'])
def handle_file_input(message: Message):
    chat_id = str(message.chat.id)
    user = get_user_by_id(chat_id)
    file = bot.download_file(bot.get_file(message.document.file_id).file_path)
    inn_list = parse_excel(file)
    info = get_info(inn_list, file, user, 'https://t.me/s7moc85ll_bot_bot')

    bot.send_message(
        chat_id,
        ' '.join(info)
    )


@bot.message_handler(content_types=['text'])
def handle_user_input(message: Message):
    chat_id = str(message.chat.id)
    user = get_user_by_id(chat_id)
    user_condition = BotUserCondition.objects.filter(user=user)[0]

    if user is not None and user_condition is not None:
        if not user.completed:
            if check_user_message(message.text):
                if user_condition.on_api_id_input:
                    bot.send_message(
                        chat_id,
                        TEXTS['/start'][1],
                        parse_mode='html',
                    )

                    user.api_id = message.text
                    user_condition.on_api_id_input = False
                    user_condition.on_api_hash_input = True

                elif user_condition.on_api_hash_input:
                    bot.send_message(
                        chat_id,
                        'Отправьте мне эксель таблицу',
                        parse_mode='html',
                    )

                    user.api_hash = message.text
                    user_condition.on_api_hash_input = False
                    user.completed = True
            else:
                bot.send_message(
                    chat_id,
                    "Данные введены некорректно, попробуйте снова",
                    parse_mode='html',
                )

        user_condition.save()
        user.save()
