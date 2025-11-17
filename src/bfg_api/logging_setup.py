import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import structlog

LOG_FILE = Path("logs/bfg.log")
MAX_BYTES = 5_000_000
BACKUP_COUNT = 5


def configure_structlog():
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    structlog.configure(
        processors=[
            timestamper,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # --- Setup standard logging handlers ---
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        # Console handler (pretty)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            structlog.stdlib.ProcessorFormatter(
                processor=structlog.dev.ConsoleRenderer(),
                foreign_pre_chain=[
                    timestamper,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.add_logger_name,
                ],
            )
        )

        # File handler (JSON)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
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

        # Root logger: WARNING+ globally (suppress info/debug)
        root_logger.setLevel(logging.WARNING)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
