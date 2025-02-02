import json
import inspect
import os
import socket
import websockets

from back_app.settings.settings import TESTS_RESULT_FILE
from back_app.settings.schema import RequestResult


def get_local_ip():
    """Получение локального ip адреса хоста"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
        return local_ip
    except Exception as error:
        print(error)
        return '0.0.0.0'


def get_name_current_func():
    """Getting a name of current function"""
    func = inspect.currentframe().f_back.f_code
    return ("%s in %s:%i" % (
        func.co_name, 
        func.co_filename, 
        func.co_firstlineno
    ))


async def send_message_to_front_by_gate(
    device_manager,
    ws_gate_url,
    to_front_message
):
    func_recieve_message = '1'
    try:
        async with websockets.connect(ws_gate_url, max_size=100048576) as websocket:
            counter = 10
            while int(func_recieve_message) != 200 and counter > 0:
                await websocket.send(to_front_message)
                func_recieve_message = json.loads(await websocket.recv())
                if not func_recieve_message: #  or not func_recieve_message.isdigit():
                    func_recieve_message = "1"
                counter -= 1
            print(f"{get_name_current_func()} - message {func_recieve_message} has been sent")
            return RequestResult(
                status_code=200,
                details=(f'Message {to_front_message} has been sent')
            )
    except Exception as error:
        print(f"{get_name_current_func()} - ERROR - {error}. Error has appeared when sent the message {func_recieve_message}")
        return RequestResult(
            status_code=500,
            details=str(error)
        )


# async def saving_results(tests_result):

#     current_order = sync_get_internal_order()

#     with open(f'temp/{TESTS_RESULT_FILE}{current_order["id"]}.log', 'a', encoding='utf-8') as file:
#         file.writelines(f'{tests_result}\n')


async def delete_result_file():
    if os.path.exists(TESTS_RESULT_FILE):
        os.remove(TESTS_RESULT_FILE)


async def def_state_read(key, device_manager):

    if not device_manager.db_adapter.sync_healthcheck():
        device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
        raise Exception(f"{get_name_current_func()} - Redis is not working.")
    else:
        def_state = await device_manager.db_adapter.get_value(key)

    return def_state


async def def_state_write(key, value, device_manager):

    if not device_manager.db_adapter.sync_healthcheck():
        device_manager.db_adapter.logger.log_error(f"{get_name_current_func()} - Redis is not working.")
        raise Exception(f"{get_name_current_func()} - Redis is not working.")
    else:
        await device_manager.db_adapter.set_value(key, value, ex=36000)
