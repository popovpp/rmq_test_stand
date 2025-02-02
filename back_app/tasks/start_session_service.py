import asyncio
import json
import threading

from back_app.tasks.initialisation_tasks import getting_rmq_code, update_internal_order
# from back_app.tasks.qr_code_tasks import make_qr
from back_app.settings.rabbitmq_connection import RmqConnection, creating_rmq_connection
from back_app.tasks.rq_tasks import sync_singl_def
from back_app.utils.utils import (send_message_to_front_by_gate, get_local_ip)
from back_app.settings.settings import RUNNING_TESTS_PORT


async def start_session(
    websocket
):

    str_current_order = await websocket.recv()
    await websocket.send("200")

    current_order = json.loads(str_current_order)
    print(current_order)

    async def starting_session_block():

        rmq_code, rmq_code_status_code = await getting_rmq_code(current_order["id"])

        if rmq_code_status_code != 200:
            raise Exception(f"The call to 'https://robotics-api.nsys-robotics.com' has got the status_code {rmq_code_status_code}")
        else:
            await update_internal_order(current_order["id"], {"queue_code": rmq_code})
            # await make_qr(str({"queue_code": rmq_code}), current_order["id"])
            # RmqConnection.close()
            # rmq_connection = RmqConnection(rmq_code)
            # print(rmq_connection.__dict__)
            await send_message_to_front_by_gate(None, f"ws://{get_local_ip()}:{RUNNING_TESTS_PORT}", json.dumps(
                {"tests_list": [],
                "current_order_id": current_order["id"]
                }
            ))

    # def run_loop(loop):
    #     asyncio.set_event_loop(loop)
    #     loop.run_forever()

    await starting_session_block()
    # # threading.Thread(target=sync_singl_def, args=(starting_session_block,), name=f"starting_session_block-{current_order["id"]}").start()
    # # task.start()
    # # task.join()

    # # loop = asyncio.get_event_loop()
    # # loop.close()
    # # if asyncio.get_event_loop().is_closed():
    # #     loop = asyncio.new_event_loop()

    # #     # Schedule the first call to display_date()
    # #     # loop.call_soon(starting_session_block, loop)
    # #     asyncio.run(starting_session_block())

    # #     # Blocking call interrupted by loop.stop()
    # #     try:
    # #         loop.run_forever()
    # #     finally:
    # #         loop.close()

    # event_loop_a = asyncio.new_event_loop()

    # task = threading.Thread(target=lambda: run_loop(event_loop_a))
    # task.start()

    # # event_loop_a.call_soon_threadsafe(lambda: starting_session_block())

    # # event_loop_a.call_soon_threadsafe(event_loop_a.stop)

    # asyncio.run_coroutine_threadsafe(starting_session_block(), event_loop_a).result()

    # task.join()

    # # result = future.result()
