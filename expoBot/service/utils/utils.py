import asyncio
import re
import time

import numpy as np
import pandas as pd
from telethon.sync import TelegramClient

from expoBot.models import BotUser


class TelethonAPI:
    def __init__(self, api_id: int, api_hash: str, phone: str):
        self.phone = phone
        self.code: str | None = None
        self.api_id = api_id
        self.api_hash = api_hash
        self.client: TelegramClient | None = None

    async def _get_client(self) -> bool:
        if self.client is None:
            self.client = TelegramClient(
                'EXPO_BOT_SESSION',
                self.api_id,
                self.api_hash,
            )
            await self.client.connect()

            # print(await self.client.is_user_authorized())

            if await self.client.is_user_authorized():
                # await self.client.start()
                return True
            return False
        return True

    async def send_code(self):
        # await self._get_client()
        # await self.client.connect()
        return await self.client.send_code_request(self.phone)

    async def login(self, phone_code_hash: str):
        # await self._get_client()
        await self.client.sign_in(
            phone=self.phone,
            code=self.code,
            phone_code_hash=phone_code_hash,
        )

    async def get_history(self, chat: str):
        return await self.client.get_messages(chat)

    async def write_a_message(self, message: str, to: str):
        # await self._get_client()
        # entity = await self.client.get_entity(to)

        await self.client.send_message(entity=to, message=message)

        # await self.client.send_message(
        #     entity=entity,
        #     message=message,
        # )
    def disconnect(self):
        self.client.disconnect()


def synchronize_async_helper(to_await: callable) -> any:
    async_response = []

    async def run_and_capture_result():
        r = await to_await
        async_response.append(r)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    coroutine = run_and_capture_result()
    loop.run_until_complete(coroutine)
    return async_response[0]


def check_user_message(data: str, email: bool = False) -> bool:
    pattern = "[A-Za-zА-Я0-9]"

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
    import io
    df = pd.ExcelFile(io.BytesIO(file)).parse(index_col=0)
    return df.index.tolist()


#def parse_excel(file: bytes) -> list[str]:
#    df = pd.ExcelFile(file).parse(index_col=0)
#    return df.index.tolist()
    # data = pd.read_excel(file, index_col=0)
    # data['Телефон'] = np.nan
    # data.to_excel(file, index=False)
    # print(data.loc['ИНН'])
    # return data.loc['ИНН'].tolist()


def parse_eye_of_god(file: bytes, text: str, inn: str):
    data = pd.read_excel(file)
    numbers = re.findall(r'\d{11}', text)
    numbers = ', '.join(map(str, numbers))
    data.loc[data['ИНН'] == inn, ['Телефон']] = numbers
    # data.to_excel(file, index=False)
    return file


def telegram_auth_check(user: BotUser, api: TelethonAPI) -> bool:
    # api = TelethonAPI(int(user.api_id), user.api_hash, user.phone_number)
    data = synchronize_async_helper(api._get_client())
    print(data)
    if not data:
        return False
    return True


def send_code(user: BotUser, api: TelethonAPI) -> str:
    # api = TelethonAPI(int(user.api_id), user.api_hash, user.phone_number)
    code_request = synchronize_async_helper(api.send_code())
    api.disconnect()
    return code_request.phone_code_hash


def telegram_auth(user: BotUser, code: str, phone_code_hash: str, api: TelethonAPI) -> str | None:
    try:
        # api = TelethonAPI(int(user.api_id), user.api_hash, user.phone_number)
        # data = synchronize_async_helper(api._get_client())
        api.code = code
        synchronize_async_helper(api.login(phone_code_hash))
        api.disconnect()
        return 'Аутентификация прошла успешно'
    except Exception as e:
        return str(e)


async def get_info(inn_list: list[str], file: bytes, user: BotUser, chat_name: str, api: TelethonAPI) -> list[str]:
    result: list[str] = []

    # api = TelethonAPI(int(user.api_id), user.api_hash, user.phone_number)
    await api._get_client()

    for inn in inn_list:
        await api.write_a_message(f'/inn {inn}', chat_name)
        time.sleep(3)
        data = await api.get_history(chat_name)
        result.append(str(data))

    api.disconnect()
    return result


#
# data = synchronize_async_helper(api._get_client())
# print('data:', data)
# if not data:
#     phone_hash = synchronize_async_helper(api.send_code())
#     api.code = input('Enter the code')
#     synchronize_async_helper(api.login(phone_hash.phone_code_hash))
#
# synchronize_async_helper(api.write_a_message('Мяффф', '@uvipp'))
# print(synchronize_async_helper(api.get_history('@uvipp')))
