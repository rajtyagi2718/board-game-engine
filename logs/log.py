from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

LOGDIR = Path('logs/')
LOGDIR.mkdir(parents=True, exist_ok=True)
LOGFORMATTER = logging.Formatter(
    fmt='%(asctime)s\t%(name)s\t%(funcName)s\n%(message)s', 
    datefmt='%H:%M:%S')

def get_logger(name):
    """Return logger instance with two file handlers and global formatter."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG) 
    handler_debug = RotatingFileHandler(
        LOGDIR/(name+'.debug.txt'), 'w', maxBytes=10*1024*1024, backupCount=5)
    handler_info = RotatingFileHandler(
        LOGDIR/(name+'.info.txt'), 'w', maxBytes=10*1024*1024, backupCount=5)
    handler_debug.setFormatter(LOGFORMATTER)
    handler_info.setFormatter(LOGFORMATTER)
    handler_debug.setLevel(logging.DEBUG)
    handler_info.setLevel(logging.INFO)
    logger.addHandler(handler_debug)
    logger.addHandler(handler_info)
    return logger
