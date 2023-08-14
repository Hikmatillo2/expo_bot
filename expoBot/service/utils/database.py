from types import NoneType

from expoBot.models import *


def check_user_exists(telegram_id: str) -> bool:
    user: [BotUser] = BotUser.objects.filter(telegram_id=telegram_id)

    if len(user) == 0:
        return False

    if len(user) == 1:
        return True


def get_user_by_id(telegram_id: str) -> BotUser | None:
    user: [BotUser] = BotUser.objects.filter(telegram_id=telegram_id)

    if len(user) == 0:
        return None

    if len(user) == 1:
        return user[0]


def add_user(telegram_id: str, nickname: str) -> bool | None:
    user = BotUser()
    user.telegram_id = telegram_id
    user.nickname = nickname
    user.save()

    try:
        user_condition = BotUserCondition()
        user_condition.user = BotUser.objects.get(telegram_id=telegram_id)
        user_condition.save()
    except Exception:
        user = BotUser.objects.get(telegram_id=telegram_id)
        user.delete()

        return None

    return True
