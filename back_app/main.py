import time
import subprocess

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from datetime import datetime
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from back_app.settings.settings import (APP_OPENAPI_URL, APP_DESCRIPTION, APP_TITLE,
                                        APP_VERSION, URL_PREFIX, REDIS_HOST, RUNNING_TESTS_PORT,
                                        SAVE_RES_TO_FILE_PORT, START_SESSION_PORT)
from back_app.settings.schema import Error, ErrorField
from back_app.settings.rq_connection import kill_all_rqworkers
from back_app.settings.rq_connection import (rq_conn_3,  rq_conn_4, rq_conn_5)
from back_app.tasks.rq_tasks import (sync_singl_def, ws_server)
from back_app.tasks.running_tests_service import running_tests
from back_app.tasks.saving_to_file_service import save_res_to_file
from back_app.utils.utils import get_local_ip
from back_app.devices.devices import DeviceManager
from back_app.devices.config.containers import get_device_manager_instance
from back_app.api.urls import router as api_router
from back_app.tasks.start_session_service import start_session


@asynccontextmanager
async def lifespan(app: FastAPI,
                   device_manager: DeviceManager = get_device_manager_instance()):
    """
    Аналог декораторов up и shutdown.
    Реализуют логику после запуска и перед выключением API
    """

    try:

        device_manager.logger.log_info('Привет!')

        kill_all_rqworkers()

        subprocess.Popen(["rq", "worker", "--name", "w3", "--url", f"redis://{REDIS_HOST}", "high", "default", "low", "q3"])
        subprocess.Popen(["rq", "worker", "--name", "w4", "--url", f"redis://{REDIS_HOST}", "high", "default", "low", "q4"])
        subprocess.Popen(["rq", "worker", "--name", "w5", "--url", f"redis://{REDIS_HOST}", "high", "default", "low", "q5"])
        time.sleep(5)
        rq_conn_3.enqueue(sync_singl_def, args=(ws_server, [get_local_ip(), RUNNING_TESTS_PORT, running_tests]), job_timeout=15000)
        rq_conn_4.enqueue(sync_singl_def, args=(ws_server, [get_local_ip(), SAVE_RES_TO_FILE_PORT, save_res_to_file]), job_timeout=15000)
        rq_conn_5.enqueue(sync_singl_def, args=(ws_server, [get_local_ip(), START_SESSION_PORT, start_session]), job_timeout=15000)

    except Exception as error:
        print(f"ERROR - {error}")
    yield
    kill_all_rqworkers()
    print('The app shuting down.')

app = FastAPI(
    lifespan=lifespan,
    openapi_url=APP_OPENAPI_URL,
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION
)

# Настройка CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=URL_PREFIX)


@app.get(f"{URL_PREFIX}/openapi", include_in_schema=False)
async def get_documentation():
    """Openapi documentation"""
    return get_swagger_ui_html(openapi_url=f"{URL_PREFIX}/openapi.json", title="docs")


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):

    errors = []
    for i in exc.errors():

        try:
            field = i['loc'][-1]
        except:
            field = 'unknown'

        try:
            message = i['msg'].capitalize()
        except:
            message = ''
        error_field = ErrorField(field=field, message=message)
        errors.append(error_field)

    error = Error(detail='Ошибка', errors=errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error.model_dump()  # error.dict(),
    )


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    elapsed = datetime.now() - start_time
    print(f'Process time: {int(elapsed.total_seconds() * 1000)} ms - "{request.url}"')
    return response


# if __name__ == "__main__":
#     pass
#     uvicorn.run(app, host=get_local_ip(), port=APP_PORT)
#     # uvicorn.run(app, host="0.0.0.0", port=8080)
