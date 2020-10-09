from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

LOGDIR = Path('logs/')
LOGDIR.mkdir(parents=True, exist_ok=True)
LOGFORMATTER = logging.Formatter(
    fmt='%(asctime)s\t%(name)s\t%(funcName)s\n%(message)s', 
    datefmt='%H:%M:%S')

# configure root logger
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.DEBUG)
_handler = RotatingFileHandler(
    LOGDIR / 'log.txt', 'w', maxBytes=10*1024*1024, backupCount=5)
_handler.setFormatter(LOGFORMATTER)
LOGGER.addHandler(_handler)
del _handler

def get_logger(name, level=logging.INFO):
    """Return logger instance with file handler and formatter."""
    logger = logging.getLogger(name)
    logger.setLevel(level) 
    handler = RotatingFileHandler(
        LOGDIR / (name + '.txt'), 'w', maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(LOGFORMATTER)
    logger.addHandler(handler)
    return logger
