import logging
from logging.config import dictConfig

from back_app.settings.logger import logger


class DeviceLogger:
    """Вспомогательный модуль для реализации логирования каждого из модулей."""
    def __init__(self, name='uvicorn.access', log_file='general.log', log_level=logging.INFO):
        dictConfig(logger)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

    def log_info(self, message):
        """Логирует важные события."""
        self.logger.info(message)

    def log_warning(self, message):
        """Логирует deprecated или особые события."""
        self.logger.warning(message)

    def log_error(self, message):
        """Логирует ошибки возникшие в ходе выполнения события."""
        self.logger.error(message)

    def log_debug(self, message):
        """Логирует события моков."""
        self.logger.debug(message)
