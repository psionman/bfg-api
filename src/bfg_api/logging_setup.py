import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import structlog

LOG_FILE = Path("logs/bfg.log")
MAX_BYTES = 5_000_000
BACKUP_COUNT = 5
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'


def configure_structlog():
    # --- Determine log level based on DEBUG env variable ---
    log_level = logging.DEBUG if DEBUG else logging.INFO
    # --- Standard library logging setup ---
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)  # Filter logs below this level globally

    # --- Timestamper processor for structlog ---
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    # --- Console handler (pretty print) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=[
                timestamper,
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
            ],
        )
    )

    # --- File handler (JSON format) ---
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=[
                timestamper,
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
            ],
        )
    )

    # Add handlers if not already added
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    # --- Configure structlog ---
    structlog.configure(
        processors=[
            timestamper,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    print(f"Structlog configured. DEBUG={DEBUG}, log_level={log_level}")
