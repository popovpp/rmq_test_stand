logger = {
    "version": 1,
    # "disable_existing_loggers": True,
    "formatters": {"default": {"format": "%(asctime)s-%(name)s-%(levelname)s-[%(threadName)s]-%(message)s"}},
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "level": "INFO",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": "general.log",
            "maxBytes": 30000000,
            "backupCount": 3,
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "gunicorn": {"propagate": True},
        "gunicorn.access": {"propagate": True},
        "gunicorn.error": {"propagate": True},
        "uvicorn": {"propagate": True},
        "uvicorn.access": {"propagate": True},
        "uvicorn.error": {"propagate": True},
        "APIAgb.access": {"propagate": True},
        "APIAgb.error": {"propagate": True},
        "StorageRedis.access": {"propagate": True},
        "StorageRedis.error": {"propagate": True},
        "Camera.access": {"propagate": True},
        "Camera.error": {"propagate": True},
        "Microcontroller.access": {"propagate": True},
        "Microcontroller.error": {"propagate": True},
        "Mic.access": {"propagate": True},
        "Mic.error": {"propagate": True},
        "Wifi.access": {"propagate": True},
        "Wifi.error": {"propagate": True},
        "Speaker.access": {"propagate": True},
        "Speaker.error": {"propagate": True},
        "Rq.access": {"propagate": True},
        "Rq.error": {"propagate": True},
        "DeviceManager.access": {"propagate": True},
        "DeviceManager.error": {"propagate": True},
    },
}
