import logging

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
LOG_DATEFMT = "%m/%d/%y - %H:%M:%S"
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, datefmt=LOG_DATEFMT)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
