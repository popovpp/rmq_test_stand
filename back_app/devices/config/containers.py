import os
import sys
import redis
from dependency_injector import containers, providers

from back_app.devices.adapters import StorageRedis
from back_app.devices.devices import DeviceManager
from back_app.devices.repositories import SystemQueue
from back_app.devices.config.logger import DeviceLogger
from back_app.settings.settings import (REDIS_DB, REDIS_HOST, REDIS_PORT)


logger = DeviceLogger()


class Container(containers.DeclarativeContainer):
    """ Proto-Контейнер зависимостей для Dependence Injector."""

    # определяем переменную под конфигурационный файл
    config = providers.Configuration(strict=True)
    # Очередь для сбора результатов из мультитрединга
    queue = providers.Singleton(SystemQueue)

    redis_pool = providers.Resource(
        redis.asyncio.Redis,
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        encoding="utf-8",
        decode_responses=True
    )

    sync_redis_pool = providers.Resource(
        redis.Redis,
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        encoding="utf-8",
        decode_responses=True
    )

    db_adapter = providers.Singleton(StorageRedis, client=redis_pool, sync_client=sync_redis_pool)

    # Основной модуль, через который будет реализовано взаимодействие всех модулей системы
    device_manager = providers.Singleton(
        DeviceManager,
        db_adapter=db_adapter,
        queue=queue,
    )


# Инициализация контейнера и создание инъекции к главному модулю для использования в API
# subprocess.run(["sudo", "cp", "/home/user/dev/agb-mcm/mcm_soft/utils/neuro_core/models/_bz2.cpython-311-aarch64-linux-gnu.so",
#                 "/usr/local/lib/python3.11/lib-dynload"])

DEBUG = True if ("--debug" in sys.argv) else False
if DEBUG:
    print('Debug mode ON')
    container = Container()
else:
    print('Debug mode OFF')
    container = Container()
print(os.getcwd())


device_manager_instance = container.device_manager()


def get_device_manager_instance():
    """Функция инъекции для FastAPI."""
    return device_manager_instance
