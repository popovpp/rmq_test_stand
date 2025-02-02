import time
import json
import threading

from back_app.utils.utils import (get_name_current_func, send_message_to_front_by_gate,
                                  get_local_ip, def_state_read, def_state_write)
from back_app.devices.devices import DeviceManager
from back_app.devices.config.containers import get_device_manager_instance
from back_app.settings.rabbitmq_connection import RmqConnection
from back_app.tasks.rq_tasks import sync_singl_def
from back_app.tasks.initialisation_tasks import sync_get_internal_order
from back_app.settings.settings import SAVE_RES_TO_FILE_PORT


async def running_tests(
    websocket,
    device_manager: DeviceManager = get_device_manager_instance()
):

    websocket_message = json.loads(await websocket.recv())
    await websocket.send("200")

    tests_list = websocket_message["tests_list"]

    current_order_id = websocket_message["current_order_id"]

    # def_state = await def_state_read(
    #     f"running_tests{current_order_id}",
    #     device_manager=device_manager)
    # print(def_state, '$$$$$$$$$$$$$$$$$$$$$$$$$$$$44')
    # if def_state is None:
    #     print(RmqConnection.__dict__)
    #     RmqConnection.close()
    #     await def_state_write(
    #         f"running_tests{current_order_id}",
    #         f"running_tests{current_order_id}",
    #         device_manager
    #     )

    # device_manager = get_device_manager_instance()
    # if device_manager.db_adapter.sync_healthcheck():
    #     current_order = sync_get_internal_order(current_order_id)
    #     print(current_order)
    # else:
    #     device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
    #     raise Exception(f"{get_name_current_func()} - Redis is not working.")

    # print(current_order['rmq_access_code'])
    # rmq_connection = RmqConnection(current_order['rmq_access_code'])
    # print(rmq_connection.__dict__)

    async def send_messages_to_app():

        # def_state = await def_state_read(
        #     f"running_tests{current_order_id}",
        #     device_manager=device_manager)
        # print(def_state, '$$$$$$$$$$$$$$$$$$$$$$$$$$$$44')
        # if def_state is None:
        #     print(RmqConnection.__dict__)
        #     RmqConnection.close()
        #     await def_state_write(
        #         f"running_tests{current_order_id}",
        #         f"running_tests{current_order_id}",
        #         device_manager
        #     )

        # device_manager = get_device_manager_instance()
        if device_manager.db_adapter.sync_healthcheck():
            current_order = sync_get_internal_order(current_order_id)
            print(current_order)
        else:
            device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
            raise Exception(f"{get_name_current_func()} - Redis is not working.")

        print(current_order['rmq_access_code'])
        rmq_connection = RmqConnection(current_order['rmq_access_code'])
        print(rmq_connection.__dict__)

        for test in tests_list:
            for cmd in test['cmd_list']:
                try:
                    test_result = await rmq_connection.async_app_message(mode=test['mode'], action=cmd, is_rmq_teststand=True, return_result=True)
                    await send_message_to_front_by_gate(None, f"ws://{get_local_ip()}:{SAVE_RES_TO_FILE_PORT}", json.dumps(
                        {"messages": {"sent_message": test_result[0], "receive_message": test_result[1]},
                         "current_order_id": current_order_id
                         }))
                    if 'Error' in test_result[1]:
                        break
                    time.sleep(1)
                except Exception as e:
                    device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Error - {e}")
                    raise Exception(f"{get_name_current_func()} - Error - {e}")

    threading.Thread(target=sync_singl_def, args=(send_messages_to_app,), name=f"send_messages_to_app-{current_order_id}").start()
    # await send_messages_to_app()
