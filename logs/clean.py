from pathlib import Path
import logging
import argparse

LOGDIR = Path('logs/')
LOGGER = logging.getLogger('clean') 
_formatter = logging.Formatter(fmt='%(message)s')
_handler = logging.StreamHandler()
_handler.setFormatter(_formatter)
LOGGER.addHandler(_handler)
del _formatter, _handler

KEEP = ('log.py', 'clean.py', '__init__.py')

PARSER = argparse.ArgumentParser(description='Remove log files.')
PARSER.add_argument('--verbose', '-v', 
                    action='store_true', 
                    help='verbose flag')

def clean():
    """Remove log files created at runtime."""
    args = PARSER.parse_args()
    if args.verbose:
        LOGGER.setLevel(logging.INFO)
    else:
        LOGGER.setLevel(logging.WARNING)

    LOGGER.info('cleaning started.')

    for path in LOGDIR.iterdir():
        if path.is_file() and all(keep not in str(path) for keep in KEEP):    
            path.unlink()
            LOGGER.info('remove\t{}'.format(path))
        else:
            LOGGER.info('keep\t{}'.format(path))

    LOGGER.info('logs removed!')

if __name__ == '__main__':

    clean()
