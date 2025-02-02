"""
SETTINGS

Глобальные настройки back_app's service od RMQ TestStand

"""

# Redis
# REDIS_HOST = 'localhost'
REDIS_HOST = '0.0.0.0'
# REDIS_HOST = 'redis_serv'
REDIS_PASSWORD = 'password'
REDIS_PORT = 6379
REDIS_DB = 0

CURRENT_PATH = './'

URL_PREFIX = '/api/v1'
APP_PORT = 8081

APP_OPENAPI_URL = f"{URL_PREFIX}/openapi.json"
APP_TITLE = "API of back_app"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "API of back_app"

ROBOTICS_API = 'https://robotics-api.nsys-robotics.com/services/queue'

TESTS_LIST_FILE = 'front_app/tests_list.csv'

TESTS_RESULT_FILE = 'tests_result_file'

RUNNING_TESTS_PORT = 4002

SAVE_RES_TO_FILE_PORT = 4003

START_SESSION_PORT = 4004
