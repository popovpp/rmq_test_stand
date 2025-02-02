import json
from typing import List

from fastapi import APIRouter, Depends

from back_app.devices.devices import DeviceManager
from back_app.devices.config.containers import get_device_manager_instance
from back_app.utils.utils import (send_message_to_front_by_gate, get_local_ip)
from back_app.settings.schema import (RequestResult)
from back_app.settings.responses import response_401, response_404, response_422
from back_app.tasks.initialisation_tasks import open_internal_order
from back_app.settings.settings import (START_SESSION_PORT, RUNNING_TESTS_PORT)


router = APIRouter(
    tags=['PROCESSES']
)


@router.post("/start-session",
            summary='Starting session',
            responses={401: response_401, 404: response_404, 422: response_422},
            response_model=RequestResult)
async def start_session(device_manager: DeviceManager = Depends(get_device_manager_instance)):
    """Starting session"""

    current_order = await open_internal_order(device_manager=device_manager)
    print(current_order)

    await send_message_to_front_by_gate(None, f"ws://{get_local_ip()}:{START_SESSION_PORT}", json.dumps(current_order))

    return RequestResult(
            data=current_order["id"],
            status_code=200
        )


@router.post("/start-test-list",
             summary='Getting the RMQ code',
             responses={401: response_401, 404: response_404, 422: response_422},
             response_model=RequestResult)
async def start_test_list(
    current_order_id: str,
    tests_list: List[dict]
):

    # tests_list = await get_test_list_from_file()
    print('#########################################################')
    print(tests_list)

    await send_message_to_front_by_gate(None, f"ws://{get_local_ip()}:{RUNNING_TESTS_PORT}", json.dumps(
        {"tests_list": tests_list,
         "current_order_id": current_order_id
         }
    ))

    return RequestResult(
            status_code=200
        )
