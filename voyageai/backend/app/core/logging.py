import logging
import structlog
from app.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, settings.log_level.upper(), logging.INFO)),
        processors=[
            structlog.processors.TimeStamper(fmt='iso'),
            structlog.processors.JSONRenderer(),
        ],
    )


def get_logger(name: str):
    return structlog.get_logger(name)
