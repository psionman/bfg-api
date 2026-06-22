# config/logging.py

import structlog


def setup_logging(active_modules: list[str], app_log_to_console: bool) -> dict:
    all_modules = ["views", "bidding", "application"]
    print("active_modules:", active_modules)
    print("app_log_to_console:", app_log_to_console)

    bfg_loggers = {
        f"bfg.{mod}": {
            "handlers": (
                ["file_json", "app_console"]
                if (app_log_to_console and mod in active_modules)
                else ["file_json"]
            ),
            "level": "DEBUG" if mod in active_modules else "WARNING",
            "propagate": False,
        }
        for mod in all_modules
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structlog_json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
                "foreign_pre_chain": [
                    structlog.processors.TimeStamper(fmt="iso", utc=True),
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                ],
            },
            "structlog_console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.dev.ConsoleRenderer(colors=True),
                "foreign_pre_chain": [
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                ],
            },
        },
        "handlers": {
            "file_json": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/bfg.log",
                "maxBytes": 5_000_000,
                "backupCount": 10,
                "formatter": "structlog_json",
                "level": "INFO",
            },
            "app_console": {
                "class": "logging.StreamHandler",
                "formatter": "structlog_console",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "": {
                "handlers": ["file_json"],
                "level": "WARNING",
                "propagate": False,
            },
            "django": {
                "handlers": ["file_json"],
                "level": "WARNING",
                "propagate": False,
            },
            "django.server": {
                "handlers": ["file_json"],
                "level": "INFO",
                "propagate": False,
            },
            **bfg_loggers,
        },
    }


def get_logger(module: str):
    name = f"bfg.{module.split('.')[-1]}"
    return structlog.get_logger(name)
