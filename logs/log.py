from pathlib import Path
import logging

LOGDIR = Path('logs/')
LOGDIR.mkdir(parents=True, exist_ok=True)
LOGFORMATTER = logging.Formatter(fmt='%(asctime)s\t%(funcName)s\n%(message)s', 
                                 datefmt='%H:%M:%S')

LOGGER = logging.getLogger('log')
LOGGER.setLevel(logging.DEBUG)
_handler = logging.FileHandler(LOGDIR / 'log.txt', 'w')
_handler.setFormatter(LOGFORMATTER)
LOGGER.addHandler(_handler)
del _handler

def get_logger(name, level=logging.INFO):
    """Return logger instance with file handler and formatter."""
    name = 'log.' + name
    logger = logging.getLogger(name)
    logger.setLevel(level) 
    handler = logging.FileHandler(LOGDIR / (name + '.txt'), 'w')
    handler.setFormatter(LOGFORMATTER)
    logger.addHandler(handler)
    return logger
