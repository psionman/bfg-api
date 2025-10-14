# logging_setup.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import structlog


# =================================================================
import datetime
import json

logger_bfg = logging.getLogger('bfg')

DATE_FORMAT = '%Y-%b-%d %H:%M:%S'


def log(username, action, payload=None):
    # """Create log message and return the message."""
    # log_time = datetime.datetime.now().strftime(DATE_FORMAT)
    # action_payload = f'<{action}>'
    # if payload:
    #     action_payload = f'<{action}> {json.dumps(payload)}'

    # log_text = f'{log_time} <{username}> {action_payload}'
    # logger_bfg.debug(log_text)

    # return log_text
    ...

# =================================================================


LOG_FILE_NAME = 'logging/bfg.log'
MAX_BYTES = 5_000_000
BACKUP_COUNT = 5


def psi_logger(level=logging.INFO):
    """
    Creates and configures a logger for the specified application.

    Args:
        app_name (str): The name of the application.
        level (int): The logging level (default is logging.INFO).

    Returns:
        Logger: A configured logger for the application.

    Examples:
        logger = psi_logger(logging.DEBUG)
    """

    # log_file = _log_file(app_name)
    log_file = LOG_FILE_NAME
    console_handler = _console_handler(level)
    file_handler = _file_handler(log_file, level)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    structlog.configure(
        processors=_processors(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()


def _console_handler(level=logging.INFO) -> logging.StreamHandler:
    """Return the console handler for the logger."""
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(),
            foreign_pre_chain=[structlog.processors.TimeStamper(fmt='iso')],
        )
    )
    return console_handler


def _file_handler(log_file: Path, level=logging.INFO) -> RotatingFileHandler:
    """Return the console handler for the logger."""
    file_handler = RotatingFileHandler(
        str(log_file),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=[structlog.processors.TimeStamper(fmt='iso')],
        )
    )
    return file_handler


def _processors() -> list:
    return [
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]


logger = psi_logger()
