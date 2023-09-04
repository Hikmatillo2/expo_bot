import asyncio
import io
import re
from asyncio import AbstractEventLoop

import pandas as pd
from telethon.sync import TelegramClient

import settings
from expoBot.service.utils.database import *
from expoBot.service.utils.utils import check_user_message, parse_excel, get_info, telegram_auth_check, send_code, \
    telegram_auth, synchronize_async_helper, TelethonAPI
from expoBot.service.utils.texts import TEXTS
from telebot import TeleBot, types
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
        TEXTS['warning'][0],
        parse_mode='html',
    )

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
    user_condition = BotUserCondition.objects.filter(user=user)[0]

    file = bot.download_file(bot.get_file(message.document.file_id).file_path)
    inn_list = parse_excel(file)

    result_data = pd.DataFrame()
    result_data['ИНН'] = inn_list
    result_data['Телефон'] = ''

    excel_file = io.BytesIO()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = TelegramClient(f'session_name_{chat_id}', int(user.api_id), user.api_hash, loop=loop)

    async def inner(client: TelegramClient, loop: AbstractEventLoop, execlFile: bytes | None = None):
        phone = user.phone_number

        await client.connect()

        if await client.is_user_authorized():
            result = []
            for inn in inn_list:
                await client.send_message(entity='@s7moc85ll_bot_bot', message=f'/inn {inn}')
                import time
                time.sleep(5)
                data = (await client.get_messages(entity='@s7moc85ll_bot_bot', limit=1))[0].message
                phone_number_pattern = "\\+?[1-9][0-9]{7,14}"
                phone_nums: list[str] = re.findall(phone_number_pattern, data)

                phone_nums_string = ', '.join(map(str, phone_nums))
                result_data.loc[result_data['ИНН'] == inn, ['Телефон']] = phone_nums_string

            result_data.to_excel(excel_file, index=False)
            binary_data = excel_file.getvalue()

            bot.send_document(
                chat_id,
                binary_data,
                caption='Итог'
            )

        else:
            print('not authorized')
            phone_code_hash = await client.send_code_request(phone)

            bot.send_message(
                chat_id,
                'Введите код авторизации'
            )

            def get_code_from_user(message: Message):
                nonlocal phone_code_hash
                chat_id = str(message.chat.id)
                user = get_user_by_id(chat_id)
                # user_condition = BotUserCondition.objects.filter(user=user)[0]

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                client = TelegramClient(f'session_name_{chat_id}', int(user.api_id), user.api_hash, loop=loop)

                async def inner(client: TelegramClient, loop: AbstractEventLoop):
                    nonlocal phone_code_hash
                    phone = user.phone_number

                    await client.connect()
                    if '_' in message.text:
                        print("_ in message")
                        code = ''.join(message.text.split('_'))
                        await client.sign_in(
                            phone=phone,
                            code=code,
                            phone_code_hash=phone_code_hash.phone_code_hash,
                        )

                        for inn in inn_list:
                            await client.send_message(entity='@s7moc85ll_bot_bot', message=f'/inn {inn}')
                            import time
                            time.sleep(5)
                            data = (await client.get_messages(entity='@s7moc85ll_bot_bot', limit=1))[0].message

                            phone_number_pattern = "\\+?[1-9][0-9]{7,14}"
                            phone_nums = re.findall(phone_number_pattern, data)

                            phone_nums_string = ', '.join(map(str, phone_nums))

                            result_data.loc[result_data['ИНН'] == inn, ['Телефон']] = phone_nums_string

                        result_data.to_excel(excel_file, index=False)
                        binary_data = excel_file.getvalue()

                        bot.send_document(
                            chat_id,
                            binary_data,
                            caption='Итог'
                        )
                    else:
                        bot.send_message(
                            chat_id,
                            'Введите код повторно!'
                        )
                    bot.register_next_step_handler_by_chat_id(message.chat.id, get_code_from_user)

                loop.run_until_complete(inner(client, loop))
                client.disconnect()

            bot.register_next_step_handler_by_chat_id(message.chat.id, get_code_from_user)

    loop.run_until_complete(inner(client, loop))
    client.disconnect()


@bot.message_handler(content_types=['contact'])
def contact_handler(message: Message):
    chat_id = str(message.chat.id)
    user = get_user_by_id(chat_id)
    user_condition = BotUserCondition.objects.filter(user=user)[0]

    if user is not None and user_condition is not None and user_condition.on_phone_number_input:
        bot_list = ""
        row_bot_list = list(Bot.objects.all())

        for i in range(len(row_bot_list)):
            bot_list += f"\n{i + 1}. {row_bot_list[i].entity}"

        bot.send_message(
            chat_id,
            'Отправьте мне эксель таблицу',
            parse_mode='html',
        )

        bot.send_message(
            chat_id,
            f'Перед отправкой убедитесь, чо вы приобрели подписку в следующих ботах:\n{bot_list}',
            parse_mode='html',
        )

        user.phone_number = message.contact.phone_number
        user_condition.on_phone_number_input = False
        user.completed = True

        user_condition.save()
        user.save()


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
                    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
                    keyboard.add(button_phone)

                    bot.send_message(
                        chat_id,
                        'Нажмите на кнопку, чтобы отправить мне ваш номер телефона',
                        reply_markup=keyboard,
                        parse_mode='html',
                    )

                    user.api_hash = message.text
                    user_condition.on_api_hash_input = False
                    user_condition.on_phone_number_input = True
            else:
                bot.send_message(
                    chat_id,
                    "Данные введены некорректно, попробуйте снова",
                    parse_mode='html',
                )

        user_condition.save()
        user.save()
