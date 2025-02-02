import json
import logging
import random
import time
from pprint import pformat

import pika
import pika.exceptions
import requests


class RMQ:
    """
    Класс RMQ взаимодействует с мобильными устройствами на ОС Android и IOS. Класс использует RabbitMQ для отправки
    и получения сообщений с мобильных устройств, а также для управления приложениями, получения логов, удаления данных и других операций.

    Этот класс реализует паттерн Singleton, чтобы обеспечить только один экземпляр RMQ во время выполнения.

    Атрибуты:
        host_rmq (str): Адрес сервера RabbitMQ
        receive_queue (str): Имя очереди для получения сообщений
        send_queue (str): Имя очереди для отправки сообщений
        rmq_queue (str): Общее имя очереди для RabbitMQ
        message_rmq (dict): Последнее полученное сообщение из RabbitMQ
        message_received (bool): Получено ли сообщение из RMQ
    """

    _instance = None

    THREAD_LOCK = False

    def __new__(cls, host_rmq="rabbitmq.nsys-robotics.com"):
        if cls._instance is None:
            cls._instance = super(RMQ, cls).__new__(cls)
        return cls._instance

    def __init__(self, host_rmq="rabbitmq.nsys-robotics.com"):
        if hasattr(self, "initialized"):
            self.close_connection_rmq()
            return
        self.channel = None
        self.connection = None
        self.receive_queue = None
        self.host_rmq = host_rmq
        self.send_queue = None
        self.rmq_queue = None
        self.initialized = True
        self.logger = logging.getLogger("[MAIN].[RMQ]")

    def open_connection_rmq(self) -> None:
        """
        Открывает соединение с сервером RabbitMQ, если соединение еще не открыто,
        для отправки и получения сообщений.
        """
        if not self.is_connected:
            url_params = pika.URLParameters(f"amqp://guest:guest@{self.host_rmq}:5672/")
            url_params.heartbeat = 60
            url_params.socket_timeout = 5
            url_params.blocked_connection_timeout = 75
            self.connection = pika.BlockingConnection(url_params)
            self.logger.info("Connection successfully open")
            if not self.channel or not self.channel.is_open:
                self.channel = self.connection.channel()
                self.logger.info("Channel successfully open")
            self.logger.info("Connection successfully established")

    def callback(self, method, body: bytes) -> dict:
        """
        Callback функция для обработки полученных сообщений RabbitMQ.

        Args:
            method (pika.spec.Basic.Deliver): метод доставки сообщения.
            body (bytes): тело сообщения.
        """
        try:
            message_rmq: dict = json.loads(body.decode())
            self.channel.basic_ack(delivery_tag=method.delivery_tag)
            self.channel.stop_consuming()
            return message_rmq
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode message: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in callback: {e}")

    def check_connection_and_channel(self) -> bool:
        """
        Проверяет, открыты ли соединение и канал с сервером RabbitMQ.
        """
        if self.connection and self.connection.is_open:
            try:
                self.channel.basic_publish(
                    exchange="",
                    routing_key="health_check",
                    body="check",
                    mandatory=True,
                )
                self.logger.info("Health check passed")
                return True
            except pika.exceptions.AMQPChannelError as e:
                self.logger.warning(f"Health check failed - Channel error: {e}")
            except pika.exceptions.AMQPConnectionError as e:
                self.logger.warning(f"Health check failed - Connection error: {e}")
            except pika.exceptions.AMQPError as e:
                self.logger.warning(f"Health check failed - AMQP error: {e}")
        self.logger.warning("Health check failed - Connection is not open")
        return False

    def send_message(self, message: str) -> None:
        """
        Отправляет сообщение в RabbitMQ.

        Args:
            message (str): сообщение для отправки.
        """
        self.ensure_connection()
        try:
            self.channel.basic_publish(
                exchange="",
                routing_key=self.send_queue,
                body=message,
                properties=pika.BasicProperties(delivery_mode=2),
                mandatory=True,
            )
            self.logger.info(f"RMQ send to device:\n {pformat(message)}")
        except pika.exceptions.UnroutableError:
            self.logger.error(f"Message could not be routed to queue {self.send_queue}")
            raise Exception("RMQ-005")
        except Exception as e:
            self.logger.error(f"Failed to send message to queue {self.send_queue}. {e}")
            raise Exception("RMQ-001")

    def receive_message_rmq(self, time_out=20, log_interval=1) -> dict:
        """
        Получает сообщения из RabbitMQ.
        """
        self.ensure_connection()
        try:
            id_stream = random.randint(1, 500)
            self.channel.basic_qos(prefetch_count=1)
            message_rmq = None
            start_time = time.time()
            last_log_time = start_time
            self.logger.info(f"Stream ID: {id_stream}. Start")
            while time.time() - start_time < time_out:
                try:
                    queue_state = self.channel.queue_declare(queue=self.receive_queue, passive=True)
                    message_count = queue_state.method.message_count
                    if message_count > 0:
                        self.logger.info(f"Found {message_count} message(s) in the queue.")
                        method_frame, _, body = self.channel.basic_get(queue=self.receive_queue)
                        if method_frame:
                            self.logger.info(f"Stream ID: {id_stream}. Message received")
                            message_rmq = self.callback(method_frame, body)
                            break
                    else:
                        current_time = time.time()
                        if current_time - last_log_time >= log_interval:
                            self.logger.info(f"Stream ID: {id_stream}. Message not found")
                            last_log_time = current_time
                except pika.exceptions.StreamLostError:
                    self.ensure_connection()
        except pika.exceptions.StreamLostError:
            raise Exception("RMQ-007")
        except pika.exceptions.ChannelClosedByBroker:
            raise Exception("RMQ-004")
        except Exception:
            raise Exception("RMQ-002")
        if message_rmq is None:
            self.logger.info(f"Message not received. Stream ID: {id_stream}")
            self.logger.error("Didn't expect a message from RMQ")
            self.close_connection_rmq()
            raise Exception("RMQ-001")
        if message_rmq["Message"]["app_message"].get("TestResult", None):
            check_file = message_rmq["Message"]["app_message"]["TestResult"]["Data"]
            if len(check_file) < 1000:
                self.logger.info(f"RMQ receive from device:\n{pformat(message_rmq)}")
            else:
                self.logger.info("RMQ receive from device: File inside")
        else:
            self.logger.info(f"RMQ receive from device:\n{pformat(message_rmq)}")
        return message_rmq

    def create_queue(self, message_ttl: int = 1200000, queue_expires: int = 3000000) -> None:
        """
        Создает очередь в RabbitMQ.

        Args:
            message_ttl (int): время жизни сообщения в миллисекундах.
            queue_expires (int): время до истечения очереди в миллисекундах.
        """
        try:
            self.ensure_connection()
            queue_arguments = {"x-message-ttl": message_ttl, "x-expires": queue_expires}
            self.channel.queue_declare(queue=self.send_queue, arguments=queue_arguments, durable=True)
            self.logger.info(f"Queue '{self.send_queue}' successfully created with message_ttl={message_ttl} and queue_expires={queue_expires}")
            self.channel.queue_declare(queue=self.receive_queue, arguments=queue_arguments, durable=True)
            self.logger.info(f"Queue '{self.receive_queue}' successfully created with message_ttl={message_ttl} and queue_expires={queue_expires}")
        except pika.exceptions.AMQPError as e:
            self.logger.error(f"Failed to create queue: {e}")
            raise Exception("RMQ-006")

    @property
    def is_connected(self):
        """
        Проверяет, открыто ли соединение с RabbitMQ.

        Returns:
            bool: True, если соединение открыто, иначе False.
        """
        try:
            if self.connection and self.connection.is_open:
                if not self.channel or not self.channel.is_open:
                    self.channel = self.connection.channel()
                if self.check_connection_and_channel():
                    return True
            return False
        except pika.exceptions.StreamLostError:
            self.logger.warning("Stream connection lost, reconnecting...")
            return False

    def ensure_connection(self, retry_count=3, retry_delay=5) -> None:
        """
        Гарантирует наличие соединения с RabbitMQ, пытаясь переподключиться при необходимости.

        Args:
            retry_count (int): количество попыток для переподключения
            retry_delay (int): Ожидание перед очередной попыткой подключения

        Returns:
            - Exception: при неудаче подключения после нескольких попыток.
        """
        if not self.is_connected:
            for _ in range(retry_count):
                try:
                    self.open_connection_rmq()
                    if self.is_connected:
                        self.logger.info("Connection successfully restored")
                        break
                    self.logger.error(f"Failed to check")
                    time.sleep(retry_delay)
                except Exception as e:
                    self.logger.error(f"Failed to reconnect: {e}")
                    time.sleep(retry_delay)
            else:
                self.logger.error("Failed to re-establish connection after several attempts!")
                raise Exception("RMQ-003")

    def close_connection_rmq(self) -> None:
        """
        Закрывает соединение с сервером RabbitMQ и канал, если они открыты.
        """
        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
                self.logger.info("Connection successfully closed")
            if self.channel and self.channel.is_open:
                self.channel.close()
                self.logger.info("Channel successfully closed")
        except pika.exceptions.StreamLostError:
            self.logger.info("The connection was closed")

    def app_message(self, *args, mode="", action="", is_rmq_teststand: bool = False, **kwargs) -> bool | dict:
        """
        Получает сообщение приложения из RabbitMQ.

        Args:
            mode (str): название теста.
            action (str): режим работы (START/STOP)

        Returns:
            - bool | dict: True, если не требуется возвращать результат, иначе возвращает данные сообщения.
        """

        self.logger.info('################ app_message ###################')
        self.logger.info(RMQ.THREAD_LOCK)
        self.logger.info('#####################################################')

        while RMQ.THREAD_LOCK:
            time.sleep(0.5)
        RMQ.THREAD_LOCK = True

        time.sleep(1)
        msg = {"Mode": mode, "Action": action}
        self.send_message(str(msg))
        message_rmq = self.receive_message_rmq()

        RMQ.THREAD_LOCK = False

        if not is_rmq_teststand:
            return message_rmq["Message"]["app_message"]
        else:
            return {"sent_message": msg, "receive_message": message_rmq["Message"]["app_message"]}

    async def async_app_message(self, *args, mode="", action="", is_rmq_teststand: bool = False, **kwargs) -> bool | dict:
        """
        Получает сообщение приложения из RabbitMQ.

        Args:
            mode (str): название теста.
            action (str): режим работы (START/STOP)

        Returns:
            - bool | dict: True, если не требуется возвращать результат, иначе возвращает данные сообщения.
        """

        self.logger.info('################ app_message ###################')
        self.logger.info(RMQ.THREAD_LOCK)
        self.logger.info('#####################################################')

        while RMQ.THREAD_LOCK:
            time.sleep(0.5)
        RMQ.THREAD_LOCK = True

        try:
            time.sleep(1)
            msg = {"Mode": mode, "Action": action}
            self.send_message(str(msg))
            message_rmq = self.receive_message_rmq()

            if not is_rmq_teststand:
                return message_rmq["Message"]["app_message"]
            else:
                return msg, message_rmq["Message"]["app_message"]
        except Exception as error:
            return msg, f'{None}: (Error - {str(error)})'
        finally:
            RMQ.THREAD_LOCK = False

    def get_queue_details(self) -> int | None:
        time.sleep(1)
        try:
            url = f"http://{self.host_rmq}:15672/api/queues/%2F/{self.send_queue}"
            response = requests.get(url, auth=("guest", "guest"))
            if response.status_code == 200:
                data = response.json()
                consumers_count = data.get("consumers")
                return consumers_count
        except Exception as error:
            self.logger.error(f"Error check queue {error}")
            return
