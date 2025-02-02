import json
import random
import string
import time

from back_app.devices.devices import DeviceManager
from back_app.devices.config.containers import get_device_manager_instance
from back_app.utils.utils import get_name_current_func
from back_app.settings.rmq_connection import RMQ


def creating_rmq_connection(
    rmq_access_code: str,
    device_manager: DeviceManager = get_device_manager_instance()
):
    print(f'################ create {rmq_access_code}###################')
    print(RMQ.THREAD_LOCK)
    print('#####################################################')
    while RMQ.THREAD_LOCK:
        time.sleep(0.5)
    RMQ.THREAD_LOCK = True

    rmq_connection = RMQ()
    rmq_connection.open_connection_rmq()
    # rmq_access_code = ''.join(random.choices(string.digits, k=5))
    rmq_connection.rmq_queue = {"MOBILE": f"MOBILE{rmq_access_code}", "ROBOT": f"ROBOT{rmq_access_code}"}
    rmq_connection.ensure_connection()
    rmq_connection.receive_queue = rmq_connection.rmq_queue["MOBILE"]
    rmq_connection.send_queue = rmq_connection.rmq_queue["ROBOT"]
    rmq_connection.create_queue()

    if rmq_connection.is_connected:
        RMQ.THREAD_LOCK = False
        if not device_manager.db_adapter.sync_healthcheck():
            device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
            raise Exception('Redis is not working.')
        else:
            return rmq_connection
    else:
        raise Exception(str("The connection with Rabbit MQ is absent"))


def open_rmq_connection(
    rmq_access_code
):

    print(f'################ open {rmq_access_code}###################')
    print(RMQ.THREAD_LOCK)
    print('#####################################################')
    while RMQ.THREAD_LOCK:
        time.sleep(0.5)
    RMQ.THREAD_LOCK = True

    rmq_connection = RMQ()
    # rmq_connection.open_connection_rmq()
    rmq_connection.rmq_queue = {"MOBILE": f"MOBILE{rmq_access_code}", "ROBOT": f"ROBOT{rmq_access_code}"}
    rmq_connection.ensure_connection()
    rmq_connection.receive_queue = rmq_connection.rmq_queue["MOBILE"]
    rmq_connection.send_queue = rmq_connection.rmq_queue["ROBOT"]

    RMQ.THREAD_LOCK = False

    return rmq_connection


class RmqConnection():

    _instance = None

    def __new__(cls, rmq_secret_code):
        if cls._instance is None:
            cls._instance = creating_rmq_connection(rmq_secret_code)
        else:
            cls._instance = open_rmq_connection(rmq_secret_code)
        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance.close_connection_rmq()
            cls._instance = None
