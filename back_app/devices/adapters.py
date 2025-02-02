import json
import logging
from typing import Any, Union

import aiohttp
import redis

from back_app.settings.schema import RequestResult
from .repositories import AbstractAPI, AbstractStorage
from .config.logger import DeviceLogger


class StorageRedis(AbstractStorage):
    """
    Модуль Redis.
    Реализует интерфейс доступа (стандартный CRUD) к данным.
    """
    def __init__(self, client: redis.asyncio.Redis, sync_client=redis.Redis, logger_name="StorageRedis.access") -> None:
        self.client = client
        self.sync_client = sync_client
        self.logger = DeviceLogger(name=logger_name, log_file='general.log', log_level=logging.INFO)
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

    async def healthcheck(self) -> bool:
        """Проверка соединения с базой данных."""
        return await self.client.ping()
    
    def sync_healthcheck(self) -> bool:
        """Проверка соединения с базой данных."""
        return self.sync_client.ping()

    async def get_value(self, key) -> str:
        """Получаем значение по ключу."""
        # self.logger.log_info('Reading from Redis is normal.')
        return await self.client.get(key)
    
    def sync_get_value(self, key) -> str:
        """Получаем значение по ключу."""
        # self.logger.log_info('Reading from Redis is normal.')
        return self.sync_client.get(key)
    
    async def getset_value(self, key, new_value) -> str:
        """Set a new meaning of the key and return the old meaning of one."""
        # self.logger.log_info('Reading from Redis is normal.')
        return await self.client.getset(key, new_value)
    
    def sync_getset_value(self, key, new_value) -> str:
        """Set a new meaning of the key and return the old meaning of one."""
        # self.logger.log_info('Reading from Redis is normal.')
        return self.sync_client.getset(key, new_value)

    async def get_json_value(self, key: str, path: str = None) -> dict:
        """
        Получаем значение по ключу в json.
        Есть возможность указания конкретного ключа внутри json'а используя
        переменную path.
        Пример:
        data = {
            'dog': {
                'scientific-name' : 'Canis familiaris'
            }
        }

        r = redis.Redis()
        r.json().set('doc', '$', data)
        doc = r.json().get('doc', '$')
        dog = r.json().get('doc', '$.dog')
        scientific_name = r.json().get('doc', '$..scientific-name')
        """
        if path:
            # path = '$' + ''.join(path)
            return await self.client.json().get(key, path)
        return await self.client.json().get(key)

    async def set_json_value(self, key: str, value: Union[dict, Any], path='$') -> dict:
        """
        Создает новый json-объект в базе или дополняет уже сушествующий.
        Принимает как обычные значения так и структуры данных (списки словари).
        навигация по вложенности регулируется через переменную path.
        """
        # Преобразуйте словарь в JSON-строку, если value - это словарь
        json_value = json.dumps(value) if isinstance(value, dict) else value
        return await self.client.json().set(name=key, path=path, obj=json_value)

    async def get_list(self, list) -> list:
        """Получить список значений, по списку ключей."""
        return await self.client.mget(list)

    async def set_value(self, key, value, ex=None) -> str:
        """Добавить значение с ключем."""
        await self.client.set(key, value, ex=ex)
        return await self.client.get(key)

    def sync_set_value(self, key, value, ex=None) -> str:
        """Добавить значение с ключем."""
        self.sync_client.set(key, value, ex=ex)
        return self.sync_client.get(key)

    async def delete_value(self, key) -> Any:
        """Удаляет значение с ключем."""
        await self.client.delete(key)
        return await self.client.get(key)


class APIAgb(AbstractAPI):
    """
    Модуль API адаптер.
    Реализует интерфейс доступа (стандартный CRUD) к внешним системам.
    В качестве библиотеки выполнения запросов используется aiohttp.
    """
    def __init__(self, client: aiohttp.ClientSession, logger_name="APIAgb.access") -> None:
        self.client = client
        self.logger = DeviceLogger(logger_name, log_file='general.log', log_level=logging.INFO)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

    async def healthcheck(self, url: str, **kwargs) -> bool:
        """Проверка соединения с внешним API."""
        try:
            async with self.client.get(url, **kwargs) as response:
                if response:
                    return True
        except aiohttp.ClientError as error:
            self.logger.log_warning(error)
            return False

    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Безопасный метод API для получения информации."""
        try:
            self.response = await self.client.get(url=url, **kwargs)
            # self.response.raise_for_status()
            return RequestResult(
                data=self.response,
                status_code=self.response.status,
                details='Ok'
            )
        except aiohttp.ClientResponseError as resp_error:
            self.logger.log_error(resp_error)
            return RequestResult(
                status_code=self.response.status,
                details=str(resp_error)
            )
        except aiohttp.ClientError as error:
            self.logger.log_error(error)
            return RequestResult(
                details=str(error)
            )
        except Exception as error:
            self.logger.log_error(error)
            return RequestResult(
                details=str(error)
            )

    async def post(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Небезопасный метод API для создания информации."""
        try:
            self.response = await self.client.post(url=url, **kwargs)
            # self.response.raise_for_status()
            return RequestResult(
                data=self.response,
                status_code=self.response.status,
                details='Ok'
            )
        except aiohttp.ClientResponseError as resp_error:
            self.logger.log_error(resp_error)
            return RequestResult(
                status_code=self.response.status,
                details=str(resp_error)
            )
        except aiohttp.ClientError as error:
            self.logger.log_error(error)
            return RequestResult(
                details=str(error)
            )
        except Exception as error:
            self.logger.log_error(error)
            return RequestResult(
                details=str(error)
            )

    async def patch(self, url: str, data: dict, **kwargs) -> aiohttp.ClientResponse:
        """Небезопасный метод API для обновления части информации."""
        try:
            self.response = await self.client.patch(url=url, data=data, **kwargs)
            self.response.raise_for_status()
            return RequestResult(
                data=self.response,
                status_code=self.response.status,
                details='Ok'
            )
        except aiohttp.ClientResponseError as resp_error:
            self.logger.log_error(resp_error)
            return RequestResult(
                status_code=self.response.status,
                details=str(resp_error)
            )
        except aiohttp.ClientError as error:
            self.logger.log_error(error)
            return RequestResult(
                details=str(error)
            )
        except Exception as error:
            self.logger.log_error(error)
            return RequestResult(
                details=str(error)
            )

    async def post_healthcheck(self, url: str, **kwargs) -> bool:
        """Проверка соединения с внешним API."""
        try:
            async with self.client.post(url, **kwargs) as response:
                if response:
                    return True
        except aiohttp.ClientError as error:
            self.logger.log_error(error)
            return False

    async def close(self):
        await self.client.close()
