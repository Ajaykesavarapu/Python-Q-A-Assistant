import logging
from app.core.config import settings

def setup_logger():
    # Set logger format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("python-qa-assistant")
    return logger

logger = setup_logger()
