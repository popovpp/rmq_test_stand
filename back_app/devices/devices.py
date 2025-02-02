import logging
# import multiprocessing
# import time
# from typing import Union

# from utils.utils import get_name_current_func
from .adapters import StorageRedis
from .repositories import SystemQueue
from .config.logger import DeviceLogger


# multiprocessing.set_start_method('fork', force=True)


class DeviceManager:
    """
    Модуль DeviceManager.
    Является основным модулем AGBox, аккумулируя в себе все интерфейсы устройства.
    Предназначен для создания верхнеуровневой абстракции в которой можно реализовать
    взаимодействие нескольких модулей (например свет и фотографирование) в одном методе,
    и уже его использовать в API для предоставления функционала пользователю.
    """
    def __init__(self, db_adapter: StorageRedis,
                 queue: SystemQueue
                 ) -> None:
        print('DeviceManager')
        self.db_adapter = db_adapter
        self.queue = queue
        self.agb_api_adapter = None
        self.metadata = None

        self.logger = DeviceLogger("DeviceManager.access", log_file='general.log', log_level=logging.INFO)

    async def check_db(self):
        """Проверяем подключение к Reids."""
        return await self.db_adapter.healthcheck()
