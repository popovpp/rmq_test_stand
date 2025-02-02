import json

from back_app.tasks.initialisation_tasks import saving_results


async def save_res_to_file(
    websocket
):
    websocket_message = json.loads(await websocket.recv())
    await websocket.send("200")

    tests_result = websocket_message["messages"]

    current_order_id = websocket_message["current_order_id"]

    print(tests_result)

    await saving_results(tests_result, current_order_id)
