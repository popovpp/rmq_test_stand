from pydantic import BaseModel
from enum import Enum
from typing import Optional, Any, List
from datetime import datetime


class ErrorField(BaseModel):

    field: str = 'Название поля'
    message: Optional[str] = 'Сообщение с ошибкой'


class Error(BaseModel):

    detail: str = 'Ошибка'
    errors: Optional[list[ErrorField]]


class ErrorNotFound(BaseModel):
    detail: str = 'Не найдено'


class ErrorAction(BaseModel):
    detail: str = 'Ошибка в действии'


class Success(BaseModel):

    detail: str = 'ОК'


class ErrorUnauthorized(BaseModel):
    detail: str = 'Не авторизован'


class RequestResult(BaseModel):
    data: Optional[Any] = None
    status_code: Optional[int] = None
    details: Optional[str] = None


class TestParams(BaseModel):
    test_name: str
    mode: str
    cmd_list: Optional[List[str]] = None


class OsType(str, Enum):
    ios = 'ios'
    android = 'Android'


class AutoTests(str, Enum):
    network = "Network"
    # barometer = "Barometer"
    bluetooth = "Bluetooth"
    wifi = "WiFi"
    accelerometer = "Accelerometer"
    gyroscope = "Gyroscope"
    compass = "Compass"
    geolocation = "Geolocation"


class IosAutoTests(str, Enum):
    tele_photo_camera = "TelePhotoCamera"
    true_depth_camera = "TrueDepthCamera"
    ultra_wide_camera = "UltraWideCamera"
    face_id = "FaceID"
    geolocation = "Geolocation"
    gyroscope = "Gyroscope"
    compass = "Compass"
    accelerometer = "Accelerometer"
    barometer = "Barometer"
    sim_reader = "SIMReader"
    e_sim = "eSIM"
    network = "Network"
    bluetooth = "Bluetooth"
    wifi = "WiFi"


class DiagnosticTests(str, Enum):
    light = "Light"
    video_mic = "VideoMic"
    phone_mic = "PhoneMic"
    video_mic_quality = "VideoMicQuality"
    phone_mic_quality = "PhoneMicQuality"
    speaker = "Speaker"
    loud_speaker = "LoudSpeaker"
    speaker_quality = "SpeakerQuality"
    loud_speaker_quality = "LoudSpeakerQuality"
    lcd_defects = "LCD_Defects"
    lcd_brightness = "LCD_Brightness"
    lcd_bornout = "LCD_Bornout"
    vibro = "Vibro"


class IosDiagnosticTests(str, Enum):
    light_sensor = "Light_Sensor"
    front_mic = "FrontMic"
    bottom_mic = "BottomMic"
    video_mic = "VideoMic"
    front_mic_qualoty = "Front_Mic_Quality"
    bottom_mic_quality = "Bottom_Mic_Quality"
    video_mic_quaality = "Video_Mic_Quality"
    loud_speaker = "Loud_Speaker"
    speaker = "Speaker"
    speaker_quality = "Speaker_Quality"
    lcd_defects = "LCD_Defects"
    lcd_brightness = "LCD_Brightness"
    lcd_burnout = "LCD_Burnout"
    vibro = "Vibro"
    flash = "Flash"


class DocumentTypes(str, Enum):
    label = "Этикетка"
    diagnostic_certificate = "Сертификат Диагностики"
    bb_certificate = "Сертификат ВВ"


class AutoTestsData(BaseModel):
    phoneinfo: Optional[dict] = None
    network: Optional[dict] = None
    barometer: Optional[dict] = None
    bluetooth: Optional[dict] = None
    wifi: Optional[dict] = None
    accelerometer: Optional[dict] = None
    giroscope: Optional[dict] = None
    geolocation: Optional[dict] = None
    compass: Optional[dict] = None


class DiagnosticTestsData(BaseModel):
    light: Optional[dict] = None
    video_mic: Optional[dict] = None
    phone_mic: Optional[dict] = None
    video_mic_quality: Optional[dict] = None
    phone_mic_quality: Optional[dict] = None
    loud_speaker: Optional[dict] = None
    speaker: Optional[dict] = None
    speaker_quality: Optional[dict] = None
    lcd_defects: Optional[dict] = None
    lcd_brightness: Optional[dict] = None
    lcd_burnout: Optional[dict] = None
    vibro: Optional[dict] = None


class InternalOrder(BaseModel):

    id: Optional[str] = None
    connection_id: Optional[str] = None
    connection_id_data: Optional[dict] = {}
    creating_date: Optional[str] = None
    rmq_access_code: Optional[str] = None
    os_type: Optional[OsType] = None
    imei: Optional[str] = None
    photoset: Optional[dict] = {}
    is_process_blocked: Optional[bool] = None
    is_ejecting_needed: Optional[bool] = False
    process_stage: Optional[str] = None
    ag_result: Optional[dict] = None
    autotests_data: Optional[AutoTestsData] = {}
    diagnostic_tests_data: Optional[DiagnosticTestsData] = {}
    locks: Optional[str] = 'ESN, ESNA, Simlock, FMIP, MDM, Jail'
    test_report_link: Optional[str] = 'http://test.com/test_report.txt'
    photoset_urls: Optional[dict] = {}
    printer_name: Optional[str] = None
    robot_serial_number: Optional[str] = 'RDS00037A0001-0009-2023-42329'
    ios_device_info: Optional[dict] = None


class DiagnosticResults(BaseModel):
    passed_number: Optional[int] = None
    failed_number: Optional[int] = None
    passed_tests_list: Optional[List[str]] = None
    failed_tests_list: Optional[List[str]] = None


class AllResults(BaseModel):

    internal_order_id: Optional[str] = None
    creating_date: Optional[str] = None
    os_type: Optional[OsType] = None
    photoset: Optional[dict] = {}
    device_info: Optional[dict] = None
    autograding_result: Optional[dict] = None
    diagnostic_results: Optional[DiagnosticResults] = None
    battery: Optional[dict] = None
    not_original_components: Optional[dict] = None
    locks: Optional[str] = 'ESN, ESNA, Simlock, FMIP, MDM, Jail'
    test_report_link: Optional[str] = 'http://test.com/test_report.txt'


class RequestAllResults(RequestResult):
    data: Optional[AllResults] = None


class ConnectWifiParaams(BaseModel):
    instruction: Optional[str] = None
    ssid: str
    password: str


class ConnectWifiParaamsResult(RequestResult):
    data: Optional[ConnectWifiParaams]


class MobileAppLink(BaseModel):
    instruction: Optional[str] = None
    mobileapp_link: str


class MobileAppLinkResult(RequestResult):
    data: Optional[MobileAppLink] = None


class PairingParams(BaseModel):
    instruction: Optional[str] = None
    rmq_access_code: Optional[str] = None


class PairingParamsResult(RequestResult):
    data: Optional[PairingParams] = None


class PhonePuttingParams(BaseModel):
    instruction: Optional[str] = None
    gif_link: Optional[str] = None


class PhonePuttingParamsResult(RequestResult):
    data: Optional[PhonePuttingParams] = None


class ToFrontMessage(BaseModel):
    process_name: Optional[str] = None
    data: Optional[Any] = None
    full_mount: Optional[int] = None
    process_progress: Optional[int] = None
    process_message: Optional[str] = None
    is_error: Optional[bool] = None
    error_details: Optional[str] = None


class TestResult(BaseModel):
    result: Optional[int] = None
    Data: Optional[str] = None
    test: Optional[str] = None


class TestResultRecord(BaseModel):
    Date: Optional[str] = None
    TestResult: Optional[dict]


class BatteryInfo(BaseModel):
    capacity_design: Optional[int] = 0
    capacity_current: Optional[int] = 0
    technology: Optional[str] = ''
    temperature: Optional[int] = 0
    health: Optional[int] = 0
    cycle_count: Optional[int] = 0
    design_capacity: Optional[int] = 0
    full_charge_capacity: Optional[int] = 0
    battery_is_charging: Optional[bool] = None


class SendBatteryInfo(BaseModel):
    connectionId: Optional[str] = None
    battery: Optional[BatteryInfo] = None


class UpdateConnectionId(BaseModel):
    connectionID: Optional[str] = None
    imei: Optional[str] = None
    imeI2: Optional[str] = None
    serial: Optional[str] = None
    color: Optional[str] = None
    osVersion: Optional[str] = None
    osInfoExt: Optional[str] = None
    firmware: Optional[str] = None
    modelNumber: Optional[str] = None
    manufacturer: Optional[str] = None
    aModelNumber: Optional[str] = None
    fmip: Optional[bool] = None
    mdm: Optional[bool] = None
    deviceHack: Optional[bool] = None
    cpu: Optional[str] = None
    root: Optional[bool] = None
    frp: Optional[bool] = None
    knox: Optional[bool] = None
    spec: Optional[str] = None
    regionInfo: Optional[str] = None
    ram: Optional[int] = None
    rom: Optional[int] = None


class CamerasDirection(str, Enum):
    front_back = 'front_back'
    top = 'top'
    left_right = 'left_right'
    bottom = 'bottom'
    all = 'all'
    two = 'two'
    three = 'three'


class ItemValue(BaseModel):
    Item: Optional[str] = None
    Value: Optional[int] = None


class SensorsBottonsFingerprints(BaseModel):
    Sensors: Optional[List[ItemValue]] = None
    Buttons: Optional[List[ItemValue]] = None
    Fingerprints: Optional[List[ItemValue]] = None


class TouchScreenField(BaseModel):
    TouchScreen: Optional[List[ItemValue]]


class BrightnessField(BaseModel):
    Brightness: Optional[List[ItemValue]] = None


class LCDPixelsField(BaseModel):
    LCDPixels: Optional[List[ItemValue]] = None


class VibroSpeakersMicrophones(BaseModel):
    Vibro: Optional[List[ItemValue]] = None
    Speakers: Optional[List[ItemValue]] = None
    Microphones: Optional[List[ItemValue]] = None


class CamerasList(BaseModel):
    Cameras: Optional[List[ItemValue]] = None


class TestResults(BaseModel):
    Buttons: Optional[SensorsBottonsFingerprints] = None
    MutiTouch: Optional[TouchScreenField] = None
    TouchScreen: Optional[TouchScreenField] = None
    LCDBrightness: Optional[BrightnessField] = None
    LCD: Optional[LCDPixelsField] = None
    Audio: Optional[VibroSpeakersMicrophones] = None
    Cameras: Optional[CamerasList] = None
