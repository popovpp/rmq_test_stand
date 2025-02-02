import multiprocessing
from abc import ABC, abstractmethod


class SystemQueue:
    """Класс реализующий интерфейс очереди задач в python."""
    def __init__(self) -> None:
        self.queue = multiprocessing.Manager().Queue()

    def get_queue(self) -> multiprocessing.Queue:
        """Метод для просмотра объектов в очереди."""
        return self.queue

class AbstractCameraModule(ABC):
    def __init__(self, db_adapter, side) -> None:
        self.logger = None
        self.db_adapter = db_adapter
        self.side = side

    @abstractmethod
    def initialization(self):
        """Метод для инициализации модуля."""
        raise NotImplementedError

    @abstractmethod
    def release(self):
        raise NotImplementedError

    @abstractmethod
    def snapshot(self):
        raise NotImplementedError

    @abstractmethod
    def check_power(self):
        """Метод для проверки питания."""
        raise NotImplementedError

    @abstractmethod
    def device_information(self):
        """Метод для предоставления метаинформации."""
        raise NotImplementedError

    @abstractmethod
    def update_firmware(self):
        """Метод для обновления интерфейса для взаимодействия с контроллером."""
        raise NotImplementedError


class AbstractMicrocontrollerModule(ABC):
    def __init__(self, serial, db_adapter, configuration) -> None:
        self.logger = None
        self.db_adapter = db_adapter
        self.serial = serial
        self.configuration = configuration

    @abstractmethod
    def check_power(self):
        """Метод для проверки питания."""
        raise NotImplementedError

    @abstractmethod
    def device_information(self):
        """Метод для предоставления метаинформации."""
        raise NotImplementedError

    @abstractmethod
    def update_firmware(self):
        """Метод для обновления интерфейса для взаимодействия с контроллером."""
        raise NotImplementedError


class AbstractWifiModule(ABC):
    def __init__(self, params: dict) -> None:
        self.params = params
        self.decoder = None
        self.logger = None
        self.adapter = None
        self.connection = None

    @abstractmethod
    def initialization(self):
        """Метод для инициализации модуля."""
        raise NotImplementedError

    @abstractmethod
    def check_power(self):
        """Метод для проверки питания."""
        raise NotImplementedError

    @abstractmethod
    def device_information(self):
        """Метод для предоставления метаинформации."""
        raise NotImplementedError

    @abstractmethod
    def update_firmware(self):
        """Метод для обновления интерфейса для взаимодействия с контроллером."""
        raise NotImplementedError


class AbstractMicModule(ABC):
    def __init__(self, params) -> None:
        self.params = params
        self.decoder = None
        self.logger = None
        self.adapter = None
        self.connection = None

    @abstractmethod
    def initialization(self):
        """Метод для инициализации модуля."""
        raise NotImplementedError

    @abstractmethod
    def check_power(self):
        """Метод для проверки питания."""
        raise NotImplementedError

    @abstractmethod
    def device_information(self):
        """Метод для предоставления метаинформации."""
        raise NotImplementedError

    @abstractmethod
    def update_firmware(self):
        """Метод для обновления интерфейса для взаимодействия с контроллером."""
        raise NotImplementedError


class AbstractSpeakerModule(ABC):
    def __init__(self) -> None:
        self.decoder = None
        self.logger = None
        self.adapter = None
        self.connection = None

    @abstractmethod
    def initialization(self):
        """Метод для инициализации модуля."""
        raise NotImplementedError

    @abstractmethod
    def check_power(self):
        """Метод для проверки питания."""
        raise NotImplementedError

    @abstractmethod
    def device_information(self):
        """Метод для предоставления метаинформации."""
        raise NotImplementedError

    @abstractmethod
    def update_firmware(self):
        """Метод для обновления интерфейса для взаимодействия с контроллером."""
        raise NotImplementedError


class AbstractStorage(ABC):
    def __init__(self, client) -> None:
        self.client = client
        self.logger = None

    @abstractmethod
    def healthcheck(self, *args, **kwargs):
        """Метод для проверки состояния соединения."""
        raise NotImplementedError

    @abstractmethod
    def get_value(self, *args, **kwargs):
        """Метод для получения данных."""
        raise NotImplementedError

    @abstractmethod
    def get_list(self, *args, **kwargs):
        """Метод для создания данных."""
        raise NotImplementedError

    @abstractmethod
    def set_value(self, *args, **kwargs):
        """Метод для изменения данных."""
        raise NotImplementedError


class AbstractAPI(ABC):
    def __init__(self, client) -> None:
        self.client = client
        self.logger = None

    @abstractmethod
    async def healthcheck(self, *args, **kwargs):
        """Метод для проверки состояния соединения."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, *args, **kwargs):
        """Метод для получения данных."""
        raise NotImplementedError

    @abstractmethod
    async def post(self, *args, **kwargs):
        """Метод для создания данных."""
        raise NotImplementedError

    @abstractmethod
    async def patch(self, *args, **kwargs):
        """Метод для изменения данных."""
        raise NotImplementedError
