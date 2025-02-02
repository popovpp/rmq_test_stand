import aiohttp
import csv
import json
from typing import List
import uuid
from datetime import datetime

from back_app.devices.adapters import APIAgb
from back_app.devices.devices import DeviceManager
from back_app.devices.config.containers import get_device_manager_instance
from back_app.settings.settings import (ROBOTICS_API, TESTS_LIST_FILE, TESTS_RESULT_FILE)
from back_app.settings.schema import TestParams, InternalOrder
from back_app.utils.utils import get_name_current_func


async def getting_rmq_code(current_order_id: str, device_manager: DeviceManager = get_device_manager_instance(),
                           is_forced=False):
    """Получение пятизначного кода для подключения к Rabbit MQ"""

    async with APIAgb(client=aiohttp.ClientSession()) as session:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        try:
            result = await session.post(
                url=ROBOTICS_API,
                data=json.dumps({
                    "serial_number": 'RDS00096A0001-0125-2024-54151',
                    "wifi_name": 'Robot-Reeva-96',
                    "wifi_password": '11223344',
                    "broker_type": 'global',
                    "broker_url": 'amqp://guest:guest@rabbitmq.nsys-robotics.com:5672'
                }),
                headers=headers
            )

        except Exception as error:
            session.logger.log_error(error)
            return None, 500

        if result.data != None:
            rmq_access_code = (await result.data.json()).get('queue_code', None)
            session.logger.log_info(f"{get_name_current_func()} - The reqquest has been done.")
            print(rmq_access_code)
            if not device_manager.db_adapter.sync_healthcheck():
                device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
                raise Exception('Redis is not working.')
            else:
                current_order = json.loads(device_manager.db_adapter.sync_get_value(current_order_id))
                if rmq_access_code is not None:
                    current_order['rmq_access_code'] = rmq_access_code
                device_manager.db_adapter.sync_set_value(current_order_id, json.dumps(current_order))
                device_manager.db_adapter.logger.log_info(
                    f'{get_name_current_func()} -The FIVE_SIGNS_CODE has been set into the CURRENT_ORDER with id = {current_order["id"]}.'
                )
            return rmq_access_code, result.status_code
        else:
            session.logger.log_error(f"{get_name_current_func()} - The call to 'https://robotics-api.nsys-robotics.com' has got a response None")
            return None, result.status_code


async def get_test_list_from_file() -> List[dict]:
    tests_list = []
    with open(TESTS_LIST_FILE, encoding='utf-8') as r_file:
        # Создаем объект reader, указываем символ-разделитель ","
        file_reader = csv.reader(r_file, delimiter=",")
        # Счетчик для подсчета количества строк и вывода заголовков столбцов
        count = 0
        # Считывание данных из CSV файла
        for row in file_reader:
            test_obj = TestParams(
                test_name=row[0].strip(),
                mode=row[1].strip(),
                cmd_list=[]
            )
            for i in range(2, len(row)):
                test_obj.cmd_list.append(row[i].strip())
            tests_list.append(test_obj.__dict__)
            count += 1
        print(f'Всего в файле {count} строк.')
    return tests_list


async def open_internal_order(
    device_manager: DeviceManager = get_device_manager_instance()
):

    current_order = InternalOrder(
        id=str(uuid.uuid1()),
        creating_date=datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    )

    if not await device_manager.db_adapter.healthcheck():
        device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
        return None
    else:
        await device_manager.db_adapter.set_value(current_order.id, json.dumps(current_order.__dict__), ex=36000)
        device_manager.db_adapter.logger.log_info(
            f'{get_name_current_func()} - Created CURRENT_ORDER with id = {current_order.id}.'
        )

        return current_order.__dict__


def get_internal_order(
    current_order_id: str,
    device_manager: DeviceManager = get_device_manager_instance()
):

    if not device_manager.db_adapter.sync_healthcheck():
        device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
        return None
    else:
        current_order = device_manager.db_adapter.sync_get_value(current_order_id)
        if current_order is not None:
            return json.loads(current_order)

    return None


async def update_internal_order(
    current_order_id: str,
    added_fields: dict,
    device_manager: DeviceManager = get_device_manager_instance()
):

    current_order = get_internal_order(current_order_id)

    if current_order is not None:
        for key in added_fields.keys():
            current_order[key] = added_fields[key]

        if not await device_manager.db_adapter.healthcheck():
            device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
            # return None
        else:
            await device_manager.db_adapter.set_value(current_order["id"],json.dumps(current_order), ex=36000)

    return current_order


def sync_get_internal_order(
    current_order_id: str,
    device_manager: DeviceManager = get_device_manager_instance()
):
    if not device_manager.db_adapter.sync_healthcheck():
        device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
        raise Exception(f"{get_name_current_func()} - Redis is not working.")
    else:
        current_order = device_manager.db_adapter.sync_get_value(current_order_id)
        if current_order is None:
            current_order = InternalOrder(
                id=str(uuid.uuid1()),
                creating_date=datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            )
            current_order = current_order.__dict__
            device_manager.db_adapter.sync_set_value(current_order_id, json.dumps(current_order))
            device_manager.db_adapter.logger.log_info(
                f'{get_name_current_func()} - Created CURRENT_ORDER with id = {current_order["id"]}.'
            )
        else:
            current_order = json.loads(current_order)

    return current_order


async def saving_results(tests_result, current_order_id):

    with open(f'temp/{TESTS_RESULT_FILE}{current_order_id}.log', 'a', encoding='utf-8') as file:
        file.writelines(f'{tests_result}\n')
