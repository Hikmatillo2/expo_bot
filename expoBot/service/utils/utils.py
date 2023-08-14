import asyncio
import re
import pandas as pd
from telethon.sync import TelegramClient

from expoBot.models import BotUser


def synchronize_async_helper(to_await: callable) -> any:
    async_response = []

    async def run_and_capture_result():
        r = await to_await
        async_response.append(r)

    loop = asyncio.get_event_loop()
    coroutine = run_and_capture_result()
    loop.run_until_complete(coroutine)
    return async_response[0]


def check_user_message(data: str, email: bool = False) -> bool:
    pattern = "[A-Za-zА-Яа-я-'@.]"

    if email:
        pattern = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if re.fullmatch(pattern, data):
            return True
    else:
        result = re.findall(pattern, data)
        if len(result) == len(data):
            return True

    return False


def parse_excel(file: bytes) -> list[str]:
    data = pd.read_excel(file, index_col=0)
    return data['ИНН'].tolist()


def get_info(inn_list: list[str], file: bytes, user: BotUser, chat_name: str) -> list[str]:
    result: list[str] = []

    api = TelethonAPI(
        int(user.api_id),
        user.api_hash,
    )

    for inn in inn_list:
        synchronize_async_helper(api.write_a_message(inn, chat_name))
        result.append(synchronize_async_helper(api.get_history(chat_name))[0])

    return result


class TelethonAPI:
    def __init__(self, api_id: int, api_hash: str):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client: TelegramClient | None = None

        self._get_client()

    def _get_client(self):
        if self.client is None:
            self.client = TelegramClient(
                'EXPO_BOT_SESSION',
                self.api_id,
                self.api_hash,
            )
            self.client.start()

    async def get_history(self, chat: str):
        return await self.client.get_messages(chat)

    async def write_a_message(self, message: str, to: str, ):
        entity = await self.client.get_entity(to)
        await self.client.send_message(
            entity=entity,
            message=message,
        )
